"""Test verileri ekle"""
import sqlite3
import uuid
import hashlib

db = sqlite3.connect("dijital_gardrop.db")
db.row_factory = sqlite3.Row

# Mevcut kullanicilari listele
users = db.execute("SELECT user_id, email, username FROM users").fetchall()
print("=== Mevcut Kullanicilar ===")
for u in users:
    print(f"  {u['user_id']} | {u['email']} | {u['username']}")

if not users:
    print("Hic kullanici yok!")
    db.close()
    exit()

# Ilk kullanici
main_user = users[0]
main_uid = main_user["user_id"]
print(f"\nAna kullanici: {main_uid}")

# Test kullanicisi olustur (eger yoksa)
test_uid = "test-user-fashionista"
existing = db.execute("SELECT user_id FROM users WHERE user_id = ?", (test_uid,)).fetchone()
if not existing:
    pw_hash = hashlib.sha256("test1234".encode()).hexdigest()
    db.execute(
        "INSERT INTO users (user_id, username, email, password_hash, display_name, bio) VALUES (?,?,?,?,?,?)",
        (test_uid, "fashionista", "fashionista@test.com", pw_hash, "Moda Tutkunu", "Tarz benim isim")
    )
    print("Test kullanicisi 'fashionista' olusturuldu.")

# Test kullanicisi 2
test_uid2 = "test-user-styleguru"
existing2 = db.execute("SELECT user_id FROM users WHERE user_id = ?", (test_uid2,)).fetchone()
if not existing2:
    pw_hash = hashlib.sha256("test1234".encode()).hexdigest()
    db.execute(
        "INSERT INTO users (user_id, username, email, password_hash, display_name, bio) VALUES (?,?,?,?,?,?)",
        (test_uid2, "styleguru", "styleguru@test.com", pw_hash, "Style Guru", "Moda danismaniniz")
    )
    print("Test kullanicisi 'styleguru' olusturuldu.")

# Ana kullanicinin test kullanicilari takip etmesini sagla
try:
    db.execute("INSERT INTO follows (follower_id, following_id) VALUES (?,?)", (main_uid, test_uid))
except sqlite3.IntegrityError:
    pass
try:
    db.execute("INSERT INTO follows (follower_id, following_id) VALUES (?,?)", (main_uid, test_uid2))
except sqlite3.IntegrityError:
    pass

# Test gonderileri ekle
test_posts = [
    {
        "user_id": test_uid,
        "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600",
        "caption": "Bugunki kombin nasil olmis? #ootd #fashion"
    },
    {
        "user_id": test_uid2,
        "image_url": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=600",
        "caption": "Sonbahar modasi basliyor! Bu ceketi cok sevdim!"
    },
    {
        "user_id": test_uid,
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600",
        "caption": "Minimalist tarz her zaman kazandirir #minimal #style"
    },
    {
        "user_id": main_uid,
        "image_url": "https://images.unsplash.com/photo-1551803091-e20673f15770?w=600",
        "caption": "Benim ilk gonderim! #firstpost"
    },
    {
        "user_id": test_uid2,
        "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600",
        "caption": "Street style vibes! Sokak modasini seviyoruz!"
    },
]

count = 0
for p in test_posts:
    post_id = str(uuid.uuid4())
    db.execute(
        "INSERT INTO posts (post_id, user_id, image_url, caption, visibility) VALUES (?,?,?,?,?)",
        (post_id, p["user_id"], p["image_url"], p["caption"], "public")
    )
    count += 1
    print(f"  Gonderi eklendi: {p['caption'][:40]}...")

db.commit()
db.close()
print(f"\nToplam {count} test gonderisi basariyla eklendi!")
