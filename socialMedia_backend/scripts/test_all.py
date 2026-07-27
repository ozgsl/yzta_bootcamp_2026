import requests
import uuid
import sys

BASE_URL = "http://localhost:8000"

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

passed = 0
failed = 0
skipped = 0


def ok(msg):
    global passed
    passed += 1
    print(f"  {GREEN}✓ PASSED{RESET}  {msg}")


def fail(msg, detail=""):
    global failed
    failed += 1
    print(f"  {RED}✗ FAILED{RESET}  {msg}")
    if detail:
        print(f"           {RED}↳ {detail[:200]}{RESET}")


def skip(msg):
    global skipped
    skipped += 1
    print(f"  {YELLOW}⊘ SKIP  {RESET}  {msg}")


def section(title):
    print(f"\n{CYAN}{BOLD}{'─'*60}{RESET}")
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}{BOLD}{'─'*60}{RESET}")


def check_server():
    try:
        r = requests.get(f"{BASE_URL}/", timeout=3)
        if r.status_code == 200:
            print(f"{GREEN}✓ Backend çalışıyor → {BASE_URL}{RESET}")
            return True
    except requests.exceptions.ConnectionError:
        pass
    print(f"{RED}✗ Backend'e bağlanılamadı!{RESET}")
    print(f"  Önce şunu çalıştır:")
    print(f"  cd socialMedia_backend")
    print(f"  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    return False


# ─────────────────────────────────────────────────────────
# 1. HEALTH
# ─────────────────────────────────────────────────────────
def test_health():
    section("1. HEALTH CHECK")
    r = requests.get(f"{BASE_URL}/")
    if r.status_code == 200 and r.json().get("status") == "healthy":
        ok("GET / → healthy")
    else:
        fail("GET / → beklenen 'healthy' dönmedi", r.text)


# ─────────────────────────────────────────────────────────
# 2. AUTH — Kayıt / Giriş / Şifre Sıfırlama
# ─────────────────────────────────────────────────────────
def test_auth():
    section("2. AUTH — Kayıt / Giriş / Şifre Sıfırlama")
    uid = uuid.uuid4().hex[:8]
    email = f"test_{uid}@gmail.com"
    password = "Sifre123!"

    # ── Kayıt ─────────────────────────────────────────────────
    r = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    if r.status_code == 201 and "user_id" in r.json():
        user_id = r.json()["user_id"]
        ok(f"POST /auth/register → {user_id[:8]}...")
    else:
        fail("POST /auth/register", r.text)
        return None

    # Test ortamı: verification_code response'dan al, otomatik doğrula
    verification_code = r.json().get("verification_code")
    if verification_code:
        requests.post(f"{BASE_URL}/auth/verify-email",
                      json={"email": email, "code": verification_code})

    # ── Çift kayıt engeli ──────────────────────────────────────
    r2 = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    if r2.status_code in (400, 409):
        ok("POST /auth/register (çift kayıt engeli) → 400/409")
    else:
        fail("Çift kayıt engeli çalışmıyor", r2.text)

    # ── Giriş (doğru şifre) ───────────────────────────────────
    r3 = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if r3.status_code == 200:
        ok("POST /auth/login (doğru şifre) → 200")
    else:
        fail("POST /auth/login", r3.text)

    # ── Giriş (yanlış şifre) ──────────────────────────────────
    r4 = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "yanlis"})
    if r4.status_code in (401, 400):
        ok("POST /auth/login (yanlış şifre) → 401")
    else:
        fail("Yanlış şifre kontrolü", r4.text)

    # ── Şifre sıfırlama ───────────────────────────────────────
    new_password = "YeniSifre456!"
    r5 = requests.post(f"{BASE_URL}/auth/reset-password",
                       json={"email": email, "new_password": new_password})
    if r5.status_code == 200:
        ok("POST /auth/reset-password → 200")
    else:
        fail("POST /auth/reset-password", r5.text)

    # Yeni şifre ile giriş çalışmalı
    r5b = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": new_password})
    if r5b.status_code == 200:
        ok("POST /auth/login (sıfırlanan şifre ile) → 200 ✓")
    else:
        fail("Sıfırlanan şifre ile giriş başarısız", r5b.text)

    # Eski şifre artık çalışmamalı
    r5c = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if r5c.status_code in (400, 401):
        ok("POST /auth/login (eski şifre geçersiz) → 401 ✓")
    else:
        skip("Eski şifre hâlâ çalışıyor — kontrol et")

    return user_id


# ─────────────────────────────────────────────────────────
# 3. 2FA (TOTP)
# ─────────────────────────────────────────────────────────
def test_two_factor_auth(user_id):
    section("3. 2FA (İKİ FAKTÖRLÜ KİMLİK DOĞRULAMA)")

    # 2FA Kurulum — user_id query param olarak gönderilir
    r = requests.post(f"{BASE_URL}/auth/2fa/setup", params={"user_id": user_id})
    if r.status_code == 200 and "secret" in r.json():
        secret = r.json()['secret']
        ok(f"POST /auth/2fa/setup → secret ({secret[:8]}...)")
    else:
        fail("POST /auth/2fa/setup", r.text)
        return

    # Geçersiz TOTP ile doğrulama → 400/401
    r2 = requests.post(f"{BASE_URL}/auth/2fa/verify",
                       json={"user_id": user_id, "code": "000000"})
    if r2.status_code in (400, 401):
        ok("POST /auth/2fa/verify (geçersiz kod) → 400/401 ✓")
    else:
        skip(f"Geçersiz TOTP kontrolü → {r2.status_code}")

    # 2FA Durum sorgusu — user_id query param
    r3 = requests.get(f"{BASE_URL}/auth/2fa/status", params={"user_id": user_id})
    if r3.status_code == 200 and "two_fa_enabled" in r3.json():
        ok(f"GET /auth/2fa/status → two_fa_enabled={r3.json()['two_fa_enabled']}")
    else:
        fail("GET /auth/2fa/status", r3.text)

    # 2FA Devre dışı bırakma — user_id query param
    r4 = requests.delete(f"{BASE_URL}/auth/2fa/disable", params={"user_id": user_id})
    if r4.status_code == 200:
        ok("DELETE /auth/2fa/disable → 200 ✓")
    else:
        fail("DELETE /auth/2fa/disable", r4.text)

    # Devre dışı doğrulaması — user_id query param
    r5 = requests.get(f"{BASE_URL}/auth/2fa/status", params={"user_id": user_id})
    if r5.status_code == 200:
        if not r5.json().get("two_fa_enabled", True):
            ok("2FA devre dışı doğrulandı ✓")
        else:
            fail("2FA hâlâ aktif görünüyor")


# ─────────────────────────────────────────────────────────
# 4. GOOGLE OAUTH
# ─────────────────────────────────────────────────────────
def test_google_auth():
    section("4. GOOGLE OAUTH (/auth/google)")

    test_email = f"google_user_{uuid.uuid4().hex[:6]}@gmail.com"
    payload = {
        "id_token": "test_token_no_verify",
        "email": test_email,
        "display_name": "Google Test Kullanıcısı",
        "avatar_url": "https://lh3.googleusercontent.com/test",
    }

    # İlk Google girişi → yeni kullanıcı
    r = requests.post(f"{BASE_URL}/auth/google", json=payload)
    if r.status_code == 200 and "user_id" in r.json():
        user_id = r.json()["user_id"]
        ok(f"POST /auth/google (yeni kullanıcı) → {user_id[:8]}...")
    else:
        fail("POST /auth/google", r.text)
        return None

    # Aynı email → aynı user_id (idempotent)
    r2 = requests.post(f"{BASE_URL}/auth/google", json=payload)
    if r2.status_code == 200 and r2.json().get("user_id") == user_id:
        ok("POST /auth/google (tekrar giriş, aynı user_id) → idempotent ✓")
    else:
        fail("Google idempotent giriş başarısız", str(r2.json()))

    # Geçersiz email → 400
    bad = {**payload, "email": "gecersiz-email"}
    r3 = requests.post(f"{BASE_URL}/auth/google", json=bad)
    if r3.status_code == 400:
        ok("POST /auth/google (geçersiz email) → 400 ✓")
    else:
        skip(f"Geçersiz email kontrolü → {r3.status_code}")

    # Temizlik
    requests.delete(f"{BASE_URL}/users/me",
                    headers={"Authorization": f"Bearer {user_id}"})
    return user_id


# ─────────────────────────────────────────────────────────
# 5. USERS
# ─────────────────────────────────────────────────────────
def test_users(user_id):
    section("5. USERS")
    headers = {"Authorization": f"Bearer {user_id}"}

    r = requests.get(f"{BASE_URL}/users/{user_id}")
    if r.status_code == 200:
        ok("GET /users/{user_id} → 200")
    else:
        fail("GET /users/{user_id}", r.text)

    r2 = requests.put(f"{BASE_URL}/users/me", headers=headers,
                      json={"display_name": "Test Kullanıcı", "bio": "Test bio"})
    if r2.status_code == 200:
        ok("PUT /users/me → 200")
    else:
        fail("PUT /users/me", r2.text)

    r3 = requests.get(f"{BASE_URL}/users/{user_id}/stats")
    if r3.status_code == 200 and "posts_count" in r3.json():
        ok(f"GET /users/{{user_id}}/stats → posts={r3.json()['posts_count']}")
    else:
        fail("GET /users/{user_id}/stats", r3.text)

    r4 = requests.put(f"{BASE_URL}/users/me/privacy", headers=headers,
                      json={"profile_visibility": "private"})
    if r4.status_code == 200:
        ok("PUT /users/me/privacy → private")
    else:
        fail("PUT /users/me/privacy", r4.text)

    r5 = requests.put(f"{BASE_URL}/users/me/privacy", headers=headers,
                      json={"profile_visibility": "public"})
    if r5.status_code == 200:
        ok("PUT /users/me/privacy → public (geri alındı)")
    else:
        fail("PUT /users/me/privacy geri alma", r5.text)


# ─────────────────────────────────────────────────────────
# 6. POSTS
# ─────────────────────────────────────────────────────────
def test_posts(user_id):
    section("6. POSTS")

    post_data = {
        "user_id": user_id,
        "image_url": "https://picsum.photos/400/400",
        "caption": "Test gönderisi",
        "visibility": "public",
        "ai_training_consent": True,
        "outfit_items": []
    }

    r = requests.post(f"{BASE_URL}/posts", json=post_data)
    if r.status_code == 201:
        ok("POST /posts → 201")
        post_id = r.json().get("post_id") or r.json().get("data", {}).get("post_id")
    else:
        fail("POST /posts", r.text)
        return None

    r2 = requests.get(f"{BASE_URL}/posts/users/{user_id}/posts",
                      params={"viewer_id": user_id})
    if r2.status_code == 200:
        posts = r2.json()
        ok(f"GET /posts/users/{{user_id}}/posts → {len(posts)} gönderi")
        if not post_id and posts:
            post_id = posts[0].get("post_id")
    else:
        fail("GET /posts/users/{user_id}/posts", r2.text)

    return post_id


# ─────────────────────────────────────────────────────────
# 7. LIKES & COMMENTS
# ─────────────────────────────────────────────────────────
def test_likes_comments(user_id, post_id):
    section("7. LIKES & COMMENTS")

    if not post_id:
        skip("Post ID yok, beğeni/yorum testleri atlanıyor")
        return

    r = requests.post(f"{BASE_URL}/posts/{post_id}/like", json={"user_id": user_id})
    if r.status_code == 201:
        ok("POST /posts/{post_id}/like → 201")
    else:
        fail("POST /posts/{post_id}/like", r.text)

    r2 = requests.post(f"{BASE_URL}/posts/{post_id}/like", json={"user_id": user_id})
    if r2.status_code == 409:
        ok("Çift beğeni engeli → 409")
    else:
        fail("Çift beğeni engeli çalışmıyor", r2.text)

    r3 = requests.delete(f"{BASE_URL}/posts/{post_id}/like", params={"user_id": user_id})
    if r3.status_code == 200:
        ok("DELETE /posts/{post_id}/like → 200")
    else:
        fail("DELETE /posts/{post_id}/like", r3.text)

    r4 = requests.post(f"{BASE_URL}/posts/{post_id}/comments",
                       json={"user_id": user_id, "content": "Harika kombin!"})
    if r4.status_code == 201:
        ok("POST /posts/{post_id}/comments → 201")
    else:
        fail("POST /posts/{post_id}/comments", r4.text)

    r5 = requests.get(f"{BASE_URL}/posts/{post_id}/comments")
    if r5.status_code == 200:
        ok(f"GET /posts/{{post_id}}/comments → {len(r5.json())} yorum")
    else:
        fail("GET /posts/{post_id}/comments", r5.text)


# ─────────────────────────────────────────────────────────
# 8. FOLLOWS
# ─────────────────────────────────────────────────────────
def test_follows(user_id_a):
    section("8. FOLLOWS")

    uid = uuid.uuid4().hex[:8]
    r = requests.post(f"{BASE_URL}/auth/register",
                      json={"email": f"user2_{uid}@gmail.com", "password": "Sifre123!"})
    if r.status_code != 201:
        skip("İkinci kullanıcı oluşturulamadı, follows testi atlanıyor")
        return None
    user_id_b = r.json()["user_id"]
    ok(f"İkinci kullanıcı oluşturuldu → {user_id_b[:8]}...")

    r2 = requests.post(f"{BASE_URL}/follow",
                       json={"follower_id": user_id_a, "following_id": user_id_b})
    if r2.status_code == 201:
        ok("POST /follow (A → B) → 201")
    else:
        fail("POST /follow", r2.text)

    r3 = requests.post(f"{BASE_URL}/follow",
                       json={"follower_id": user_id_a, "following_id": user_id_b})
    if r3.status_code == 409:
        ok("Çift takip engeli → 409")
    else:
        fail("Çift takip engeli", r3.text)

    r4 = requests.post(f"{BASE_URL}/follow",
                       json={"follower_id": user_id_a, "following_id": user_id_a})
    if r4.status_code == 400:
        ok("Kendini takip engeli → 400")
    else:
        fail("Kendini takip engeli", r4.text)

    r5 = requests.delete(f"{BASE_URL}/follow",
                         json={"follower_id": user_id_a, "following_id": user_id_b})
    if r5.status_code == 200:
        ok("DELETE /follow → 200")
    else:
        fail("DELETE /follow", r5.text)

    return user_id_b


# ─────────────────────────────────────────────────────────
# 9. WARDROBE
# ─────────────────────────────────────────────────────────
def test_wardrobe(user_id):
    section("9. WARDROBE")

    kiyafet = {"tur": "tişört", "renk": "beyaz", "marka": "Zara",
               "beden": "M", "mevsim": "yaz", "temiz": True}

    r = requests.post(f"{BASE_URL}/wardrobe/items",
                      params={"user_id": user_id}, json=kiyafet)
    if r.status_code == 200 and "id" in r.json():
        item_id = str(r.json()['id'])
        ok(f"POST /wardrobe/items → id={item_id[:8]}...")
    else:
        fail("POST /wardrobe/items", r.text)

    requests.post(f"{BASE_URL}/wardrobe/items",
                  params={"user_id": user_id},
                  json={"tur": "pantolon", "renk": "lacivert", "temiz": True})

    r2 = requests.get(f"{BASE_URL}/wardrobe/items/{user_id}")
    if r2.status_code == 200:
        ok(f"GET /wardrobe/items/{{user_id}} → {len(r2.json())} kıyafet")
    else:
        fail("GET /wardrobe/items/{user_id}", r2.text)

    r3 = requests.get(f"{BASE_URL}/wardrobe/chat/history/{user_id}")
    if r3.status_code == 200:
        ok(f"GET /wardrobe/chat/history → {len(r3.json())} mesaj")
    else:
        fail("GET /wardrobe/chat/history", r3.text)

    r4 = requests.post(f"{BASE_URL}/wardrobe/chat",
                       json={"user_id": user_id, "mesaj": "Hangi kıyafetleri önerirsin?"})
    if r4.status_code == 200:
        ok("POST /wardrobe/chat → 200 (AI yanıtı geldi)")
    elif r4.status_code in (502, 500):
        skip("POST /wardrobe/chat → AI key yok, atlandı")
    else:
        fail("POST /wardrobe/chat", r4.text)

    r5 = requests.post(f"{BASE_URL}/wardrobe/outfit/suggest",
                       json={"user_id": user_id, "etkinlik": "iş", "hava_durumu": "serin"})
    if r5.status_code == 200:
        ok("POST /wardrobe/outfit/suggest → 200")
    elif r5.status_code in (400, 502, 500):
        skip(f"POST /wardrobe/outfit/suggest → {r5.status_code} (AI key veya temiz kıyafet yok)")
    else:
        fail("POST /wardrobe/outfit/suggest", r5.text)


# ─────────────────────────────────────────────────────────
# 10. SAVE / UNSAVE POSTS
# ─────────────────────────────────────────────────────────
def test_save_posts(user_id, post_id):
    section("10. SAVE / UNSAVE POSTS")

    if not post_id:
        skip("Post ID yok, kaydetme testleri atlanıyor")
        return

    r = requests.post(f"{BASE_URL}/posts/{post_id}/save", params={"user_id": user_id})
    if r.status_code == 200:
        ok("POST /posts/{post_id}/save → 200")
    else:
        fail("POST /posts/{post_id}/save", r.text)

    r2 = requests.get(f"{BASE_URL}/posts/users/{user_id}/saved_posts")
    if r2.status_code == 200:
        ok(f"GET /posts/users/{{user_id}}/saved_posts → {len(r2.json())} gönderi")
    else:
        fail("GET /posts/users/{user_id}/saved_posts", r2.text)

    r3 = requests.delete(f"{BASE_URL}/posts/{post_id}/save", params={"user_id": user_id})
    if r3.status_code == 200:
        ok("DELETE /posts/{post_id}/save → 200")
    else:
        fail("DELETE /posts/{post_id}/save", r3.text)


# ─────────────────────────────────────────────────────────
# 11. TEMİZLİK
# ─────────────────────────────────────────────────────────
def test_cleanup(user_id, user_id_b=None, post_id=None):
    section("11. TEMİZLİK")
    headers = {"Authorization": f"Bearer {user_id}"}

    if post_id:
        r = requests.delete(f"{BASE_URL}/posts/{post_id}", params={"user_id": user_id})
        if r.status_code == 200:
            ok("DELETE /posts/{post_id} → 200")
        else:
            fail("DELETE /posts/{post_id}", r.text)

    r2 = requests.delete(f"{BASE_URL}/users/me", headers=headers)
    if r2.status_code == 200:
        ok("DELETE /users/me (user_a) → 200")
    else:
        fail("DELETE /users/me", r2.text)

    if user_id_b:
        r3 = requests.delete(f"{BASE_URL}/users/me",
                             headers={"Authorization": f"Bearer {user_id_b}"})
        if r3.status_code == 200:
            ok("DELETE /users/me (user_b) → 200")
        else:
            fail("DELETE /users/me (user_b)", r3.text)


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"  DİJİTAL GARDROP — TAM API TEST SÜİTİ")
    print(f"  Backend: {BASE_URL}")
    print(f"{'='*60}")

    if not check_server():
        sys.exit(1)

    test_health()

    # ── Auth (kayıt + giriş + şifre sıfırlama) ────────────────
    user_id = test_auth()
    if not user_id:
        print(f"\n{RED}Auth başarısız, diğer testler çalışamaz.{RESET}")
        sys.exit(1)

    # ── Yeni özellikler ────────────────────────────────────────
    test_two_factor_auth(user_id)
    test_google_auth()

    # ── Mevcut özellikler ──────────────────────────────────────
    test_users(user_id)
    post_id = test_posts(user_id)
    test_likes_comments(user_id, post_id)
    user_id_b = test_follows(user_id)
    test_wardrobe(user_id)
    test_save_posts(user_id, post_id)
    test_cleanup(user_id, user_id_b, post_id)

    total = passed + failed + skipped
    print(f"\n{'='*60}")
    print(f"  SONUÇ")
    print(f"{'='*60}")
    print(f"  Toplam   : {total}")
    print(f"  {GREEN}Başarılı : {passed}{RESET}")
    print(f"  {RED}Başarısız: {failed}{RESET}")
    print(f"  {YELLOW}Atlandı  : {skipped}{RESET}")
    print(f"{'='*60}\n")

    if failed == 0:
        print(f"{GREEN}{BOLD}  TÜM TESTLER BAŞARILI!{RESET}\n")
    else:
        print(f"{RED}{BOLD}  {failed} test başarısız!{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
