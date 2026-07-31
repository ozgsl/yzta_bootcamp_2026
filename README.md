# Dijital Gardrop

**Yapay Zeka Destekli Moda Sosyal Medya Platformu**

> YZTA Bootcamp 2026 — Takım 35 Proje Raporu
> Ahmet Colak

Dijital Gardrop; kullanıcıların dijital gardıroplarını yönetmelerine, yapay zeka destekli kombin önerileri almalarına ve moda içeriklerini paylaşmalarına olanak tanıyan bir mobil platformdur. Sistem; **Flutter** tabanlı çok platformlu mobil istemci, **FastAPI** tabanlı RESTful arka uç ve yerel olarak çalışan **Ollama/LLaMA 3.2** dil modeli üçlüsünden oluşmaktadır.

Bu README, 4 Temmuz 2026 tarihli güncel gorev günlüğü (task log) ve sprint burndown verilerine dayanmaktadır.

---

## İçindekiler

- [Sistem Mimarisi](#sistem-mimarisi)
- [Kullanılan Teknolojiler](#kullanılan-teknolojiler)
- [Veri Modeli](#veri-modeli)
- [API Uç Noktaları](#api-uç-noktaları)
- [Yapay Zeka Entegrasyonu](#yapay-zeka-entegrasyonu)
- [Karşılaşılan Sorunlar ve Çözümler](#karşılaşılan-sorunlar-ve-çözümler)
- [Ağ Bağlantısı ve Dağıtım](#ağ-bağlantısı-ve-dağıtım)
- [Proje Yönetimi: Görev Günlüğü ve Sprint Burndown](#proje-yönetimi-görev-günlüğü-ve-sprint-burndown)
- [Sonuç](#sonuç)
- [Kaynaklar](#kaynaklar)

---

## Sistem Mimarisi

Sistem, birbirine RESTful API aracılığıyla bağlanan üç ana katmandan oluşmaktadır:

1. **İstemci Katmanı** — Flutter (Dart) ile geliştirilen iOS/Android uygulaması.
2. **Uygulama Katmanı** — Python 3.9+ ve FastAPI ile geliştirilen REST arka uç.
3. **AI Katmanı** — Yerel ağda çalışan Ollama sunucusu üzerindeki LLaMA 3.2 modeli.

## Kullanılan Teknolojiler

| Katman | Teknoloji | Sürüm |
|---|---|---|
| Mobil İstemci | Flutter | 3.10+ |
| Dil (İstemci) | Dart | 3.0+ |
| Durum Yönetimi | Riverpod | 2.4.9 |
| Görsel Önbellek | cached_network_image | 3.3+ |
| Resim Seçici | image_picker | 1.2+ |
| Oturum Kalıcılığı | shared_preferences | 2.2+ |
| REST Arka Uç | FastAPI | 0.110+ |
| Dil (Arka Uç) | Python | 3.9+ |
| Veritabanı | SQLite | 3.x |
| ASGI Sunucusu | Uvicorn | 0.29+ |
| HTTP İstemcisi | httpx | 0.27+ |
| Statik Dosyalar | FastAPI StaticFiles | — |
| Yapay Zeka | Ollama (LLaMA 3.2) | 3.2 |

## Veri Modeli

Uygulama SQLite veritabanı üzerinde şu tablolarla çalışmaktadır:

- **users** — Kullanıcı profilleri (`user_id`, `email`, `username`, `avatar`, `bio`, `followers_count`, `following_count`, `is_private`)
- **posts** — Gönderiler (`post_id`, `user_id`, `image_url`, `caption`, `visibility`, `likes_count`, `comments_count`)
- **post_outfit_items** — Gönderi–kıyafet ilişkisi (`category` CHECK kısıtı: üst giyim, alt giyim, ayakkabı, aksesuar, dış giyim, diğer)
- **kiyafetler** — Dijital gardırop kıyafetleri (tür, renk, beden, marka, mevsim, temiz, foto_url)
- **likes** — Beğeniler (`post_id`, `user_id`)
- **follows** — Takip ilişkisi (`follower_id`, `following_id`)
- **sohbetler** — AI stilist sohbet geçmişi (`user_id`, `rol`, `mesaj`, `olusturma_zamani`)
- **kombin_oneriler** — Kombin önerileri (`user_id`, `baglam_json`, `aciklama`)
- **comments** — Yorumlar (`comment_id`, `post_id`, `user_id`, `text`, `created_at`)

## API Uç Noktaları

| Grup | Endpoint | Açıklama |
|---|---|---|
| Auth | `POST /auth/login` | Giriş |
| | `POST /auth/register` | Kayıt |
| Posts | `POST /posts` | Gönderi oluştur |
| | `DELETE /posts/{id}` | Gönderi sil |
| | `GET /posts/users/{uid}/posts` | Kullanıcı gönderileri |
| Likes | `POST /posts/{id}/like` | Beğen |
| | `DELETE /posts/{id}/like` | Beğeni kaldır |
| | `POST /posts/{id}/comments` | Yorum ekle |
| | `GET /posts/{id}/comments` | Yorumları listele |
| Feed | `GET /feed` | Akış |
| Users | `GET /users/{uid}` | Profil |
| | `PUT /users/me` | Profil güncelle |
| | `PUT /users/me/privacy` | Gizlilik ayarı |
| Follows | `POST /follow` | Takip et |
| | `DELETE /follow` | Takipten çık |
| Wardrobe | `POST /wardrobe/items` | Kıyafet ekle |
| | `GET /wardrobe/items/{uid}` | Kıyafetleri listele |
| | `POST /wardrobe/chat` | AI stilist chat |
| | `GET /wardrobe/chat/history/{uid}` | Sohbet geçmişi |
| | `POST /wardrobe/outfit/suggest` | Kombin öner |
| Captions | `POST /captions/suggest` | AI açıklama öner |
| | `POST /captions/upload` | Resim yükle |
| Static | `GET /static/uploads/{file}` | Resim sun |

## Yapay Zeka Entegrasyonu

### Ollama / LLaMA 3.2

Başlangıçta Google Gemini API kullanımı planlanmış, ancak kullanıcının yerel dil modeli tercih etmesi üzerine sistem Ollama üzerindeki LLaMA 3.2 modeline geçirilmiştir. Bu geçiş şu avantajları sağlamıştır:

- **Veri gizliliği** — istemler harici sunuculara gönderilmez.
- **Sıfır API maliyeti** — harici ücretlendirme yoktur.
- **Çevrimdışı çalışma** — internet bağlantısı gerektirmez.

### AI Stilist Chatbot

AI stilist bileşeni `gemini_client.py` modülünde uygulanmıştır. Model, Türkçe sistem promptları ile yönlendirilmekte; JSON çıktı ayrıştırma başarısız olduğunda güvenli bir geri dönüş mekanizması devreye girmektedir. İki temel işlevsellik sunulmaktadır:

```python
def sohbet_yaniti_al(gecmis, yeni_mesaj):
    # Sistem promptu + gecmis + yeni mesaj
    # JSON yanit: asistan_mesaji, baglam, hazir_mi
    ...

def kombin_onerisi_uret(baglam, temiz_kiyafetler):
    # Baglam + kiyafet listesi
    # JSON yanit: secilen_idler, aciklama
    ...
```

## Karşılaşılan Sorunlar ve Çözümler

### iOS Kamera Çökmesi
**Sorun:** Kıyafet ekleme ekranında kamera butonuna basıldığında uygulama iOS'ta çöküyordu.
**Kök Neden:** `Info.plist` dosyasında `NSCameraUsageDescription` ve `NSPhotoLibraryUsageDescription` anahtarları eksikti.
**Çözüm:** Dört izin anahtarı `Info.plist`'e eklendi: `NSCameraUsageDescription`, `NSPhotoLibraryUsageDescription`, `NSPhotoLibraryAddUsageDescription`, `NSMicrophoneUsageDescription`.

### SQLite CHECK Kısıt İhlali
**Sorun:** Gönderi oluşturulurken 500 hatası: *"Check constraint failed IN ('ust giyim', 'alt giyim', ...)"*.
**Kök Neden:** `post_outfit_items` tablosuna `category = 'unknown'` değeri insert ediliyordu.
**Çözüm:** `post_repository.py` dosyasında sabit değer `'unknown'` → `'diger'` olarak güncellendi.

### Oturum Kalıcılığı Eksikliği
**Sorun:** Uygulama her açıldığında giriş ekranı gösteriliyor, kullanıcı oturumu hatırlanmıyordu.
**Kök Neden:** `AuthProvider` sınıfı yalnızca bellekte `userId` tutuyor, kalıcı depolamaya yazılmıyordu.
**Çözüm:** `shared_preferences` paketi entegre edildi. `_AuthGate` widget'ı oturum durumuna göre yönlendirme yapacak şekilde `main.dart`'a eklendi.

### Resim Yükleme Akışı
**Sorun:** Yerel dosya yolu backend'e gönderildiğinden resimler diğer cihazlarda görüntülenemiyordu.
**Çözüm:**
1. Backend'e `POST /captions/upload` multipart endpoint'i eklendi.
2. Dosya UUID adıyla `static/uploads/` dizinine kaydedildi.
3. Frontend resmi önce yüklüyor, dönen URL'yi post/kıyafet kaydına yazıyor.

### Likes/Comments 404 Hatası
**Sorun:** Beğeni ve yorum endpoint'leri 404 döndürüyordu.
**Kök Neden:** `likes.py` router'ı `main.py` dosyasına hiç dahil edilmemişti.
**Çözüm:** `main.py`'e router kayıt edildi. `POST/GET /posts/{id}/comments` endpoint'leri eklendi. DELETE beğeni query param ile `user_id` alacak şekilde güncellendi.

### AI Stilist Yanıt Sorunu
**Sorun:** AI Stilist ekranı "I could not generate response." mesajı gösteriyordu.
**Kök Neden 1:** Frontend `response['reply']` anahtarını okurken backend `asistan_mesaji` anahtarını döndürüyordu.
**Kök Neden 2:** Ekran `user_id = 'user_123'` şeklinde sabit değer kullanıyordu.
**Çözüm:** `ai_stylist_screen.dart` tamamen yeniden yazıldı; doğru JSON anahtarları, gerçek kullanıcı ID'si ve geçmiş yükleme özelliği eklendi.

### Python 3.9 Uyumluluk Sorunları
**Sorun:** Backend Python 3.10+ tip söz dizimi (`list[X]`, `str | None`) kullandığından Python 3.9 ortamında hata veriyordu.
**Çözüm:** Tüm tip ek açıklamaları `from typing import List, Optional` kullanılarak güncellendi.

### Gönderi Silme Sorunu
**Sorun:** Profil ekranındaki Sil butonu yalnızca SnackBar gösteriyor, API çağrısı yapmıyordu.
**Çözüm:** `DELETE /posts/{post_id}?user_id={uid}` endpoint'i backend'e eklendi; `profile_provider.dart`'a `deletePost` metodu eklendi.

## Ağ Bağlantısı ve Dağıtım

Uygulama geliştirme aşamasında yerel ağ üzerinde test edilmiştir. iPhone'un kişisel hotspot'u üzerinden Mac'in IP adresi (`172.20.10.13:8000`) kullanılarak bağlantı sağlanmıştır.

## Proje Yönetimi: Görev Günlüğü ve Sprint Burndown

Projenin görev takibi, görev günlüğü (task log) ve sprint burndown tablosu ile yapılmaktadır. Her görev; benzersiz bir kimlik (ID), efor puanı (story point), başlangıç/bitiş tarihi, sorumlu kişi ve ait olduğu sprint ile kayıt altına alınmaktadır.

### Görev Grupları

Görevler, ön ekine göre yedi ana gruba ayrılmıştır:

| Grup | Kapsam | Efor | Durum |
|---|---|---|---|
| F | Temeller (rol dağılımı, araştırma) | 10 | ✅ Tamamlandı |
| S | Feed / LLM / Öneri planlama | 45 | ✅ Tamamlandı |
| AP | Kimlik doğrulama & profil | 92 | ✅ Tamamlandı |
| O | Onboarding / karşılama ekranları | 38 | ✅ Tamamlandı |
| CF | Dijital gardırop (kıyafet) CRUD | — | 🕓 Planlandı |
| BU | AI stilist sohbet arayüzü | — | 🕓 Planlandı |
| G | Kombin önerisi & galeri | — | 🕓 Planlandı |

F, S, AP ve O gruplarındaki toplam **24 görev**, 19 Haziran – 4 Temmuz 2026 aralığında tamamlanmış olup **196 efor puanına** karşılık gelmektedir. Bu görevler sırasıyla:

- Proje temelleri ve ekip rol dağılımı (`F-1`)
- Sosyal medya akışı / LLM / öneri motoru için yaklaşım planlaması (`S-1`, `S-2`, `S-3`)
- Kayıt ol–giriş yap–şifre sıfırlama–token yenileme–profil güncelleme–hesap silme uçtan uca kimlik doğrulama akışı (`AP-1` – `AP-12`)
- Karşılama, onboarding adımları ve boş durum (empty-state) arayüzleri (`O-1` – `O-8`)

Sorumlular **Özge** (arayüz ve kimlik doğrulama tarafı) ve **Ahmet** (planlama ve backend tarafı) olarak paylaşılmıştır.

`CF` (dijital gardırop CRUD), `BU` (AI stilist sohbet arayüzü) ve `G` (kombin önerisi/galeri) gruplarındaki **21 görev**, görev günlüğünde tanımlanmış ancak henüz efor puanı ve tarih atanmamış durumdadır; bu görevler ilerleyen sprintlerde resmi olarak planlanacak ve burndown tablosuna dahil edilecektir. Bu görevlerin teknik altyapısı — kıyafet ekleme, kombin önerisi ve AI stilist sohbeti — yukarıdaki [Karşılaşılan Sorunlar ve Çözümler](#karşılaşılan-sorunlar-ve-çözümler) bölümünde anlatılan geliştirme çalışmaları kapsamında paralel olarak ilerletilmiştir.

### Sprint Durumu

- **Sprint 1 (19 Haziran – 5 Temmuz 2026):** F, S, AP ve O gruplarındaki tüm planlı görevler tamamlanmıştır. Sprintin resmi bitiş tarihi 5 Temmuz olup rapor tarihi (4 Temmuz) itibariyle sprint sona ermek üzeredir.
- **Sprint 2 (6 – 19 Temmuz 2026):** Sprint, "Forgot password page UI" (`AP-3`, 5 puan) görevi ile 4 Temmuz'da başlamış, görev henüz devam etmektedir (bitiş tarihi atanmamış).

### Sprint Burndown

Toplam proje kapsamı **900 efor puanı** olarak belirlenmiştir. Aşağıdaki tablo, seçilen tarihlerdeki ideal (planlanan) burndown değeri ile gerçek tamamlanan/kalan puanları karşılaştırmaktadır.

| Tarih | İdeal Kalan | Tamamlanan (Kümülatif) | Gerçek Kalan |
|---|---|---|---|
| 19 Haz | 847.1 | 0 | 900 |
| 24 Haz | 582.4 | 23.75 | 876.25 |
| 27 Haz | 423.5 | 91 | 809 |
| 30 Haz | 264.7 | 122.5 | 777.5 |
| 2 Tem | 158.8 | 160.5 | 739.5 |
| 4 Tem | 52.9 | 196 | 704 |

4 Temmuz 2026 itibariyle 900 puanlık toplam kapsamın **196 puanı (~%22'si)** tamamlanmış, **704 puan** kalan durumdadır. Gerçek kalan iş miktarının ideal burndown eğrisinin üzerinde seyretmesi, `CF`/`BU`/`G` gruplarındaki 21 görevin henüz efor puanı ile planlanmamış olmasından kaynaklanmaktadır; bu görevler resmi olarak puanlandığında toplam kapsam ve buna bağlı ideal eğri yeniden hesaplanacaktır.

## Sonuç

Yapay zeka destekli moda sosyal medya platformu Dijital Gardrop'un tasarımı ve geliştirilmesi, görev günlüğü ve sprint burndown verileriyle desteklenerek sunulmuştur. Flutter, FastAPI ve Ollama/LLaMA 3.2 teknolojilerini bir araya getiren platform; kıyafet yönetimi, kombin önerisi, sosyal etkileşim ve içerik paylaşımını entegre etmektedir.

Geliştirme sürecinde karşılaşılan teknik engeller sistematik olarak aşılmış, Sprint 1 kapsamındaki kimlik doğrulama, profil ve onboarding görevlerinin tamamı tamamlanmıştır. Sprint 2 ile birlikte odak, dijital gardırop, AI stilist sohbeti ve kombin önerisi görevlerinin resmi olarak planlanıp puanlandırılmasına kaymaktadır. Sistemin yerel yapay zeka modeliyle çalışması, veri gizliliği açısından önemli bir avantaj sunmaktadır.

## Kaynaklar

- Flutter Team, "Flutter — Build apps for any screen," Google LLC, 2024.
- S. Ramirez, "FastAPI," 2024. https://fastapi.tiangolo.com
- Ollama Team, "Ollama," 2024. https://ollama.com
- R. Rousselet, "Riverpod," 2024. https://riverpod.dev
- D. R. Hipp, "SQLite," 2024. https://sqlite.org

---

## 🚀 Projeyi Çalıştırma

### Ön Gereksinimler

| Araç | Sürüm | Kurulum |
|------|-------|---------|
| Python | 3.9+ | `brew install python` / `apt install python3` |
| Flutter | 3.10+ | https://flutter.dev/docs/get-started/install |
| Ollama | Latest | `curl -fsSL https://ollama.com/install.sh \| sh` |
| Git | Latest | `brew install git` / `apt install git` |

### 1. Ollama Modellerini İndirin

```bash
# Ollama sunucusunu başlatın (ayrı bir terminalde çalışmalı)
ollama serve

# Gerekli modelleri indirin
ollama pull moondream      # Görsel analiz (kıyafet tanıma, caption)
ollama pull llama3.2       # Metin tabanlı AI stilist sohbeti

# Modelleri kontrol edin
ollama list
```

### 2. Backend (FastAPI) Kurulumu

```bash
cd socialMedia_backend

# Sanal ortam oluşturun ve aktif edin
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install --upgrade pip
pip install -r requirements.txt

# Veritabanını başlatın
python -c "from app.core.database import init_db; init_db()"

# Backend'i başlatın (0.0.0.0 ile ağ erişimi açık)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend doğrulama:**
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/ (JSON döner)

### 3. Frontend (Flutter) Kurulumu

```bash
cd socialMedia_frontend

# Bağımlılıkları yükleyin
flutter pub get

# API base URL'yi ayarlayın (lib/core/api/api_service.dart)
# iOS Simulator: http://localhost:8000
# Android Emulator: http://10.0.2.2:8000
# Fiziksel cihaz: http://<BILGISAYAR_IP>:8000

# Uygulamayı çalıştırın
flutter devices          # Mevcut cihazları listele
flutter run -d <device_id>
```

**Hızlı başlatma örnekleri:**
```bash
# iOS Simulator
flutter run -d ios

# Android Emulator
flutter run -d android

# Chrome (Web)
flutter run -d chrome
```

### 4. İki Terminle Eşzamanlı Çalıştırma

**Terminal 1 - Backend + Ollama:**
```bash
# Terminal 1a: Ollama
ollama serve

# Terminal 1b: Backend
cd socialMedia_backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd socialMedia_frontend
flutter run -d <device_id>
```

### 5. Yaygın Sorunlar ve Çözümler

| Sorun | Çözüm |
|-------|-------|
| `ModuleNotFoundError: torch` | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu` |
| `Ollama connection refused` | `ollama serve` çalışıyor mu kontrol edin |
| Android'de `Connection refused` | `baseUrl = 'http://10.0.2.2:8000'` kullanın |
| iOS'ta `Connection refused` | `baseUrl = 'http://<MAC_IP>:8000'` kullanın (localhost değil) |
| Veritabanı kilitli | `rm socialMedia_backend/dijital_gardrop.db` ve yeniden başlatın |
| CORS hatası | `.env` dosyasında `CORS_ORIGINS` kontrol edin |

### 6. Test Etme

```bash
# Backend testleri
cd socialMedia_backend
source venv/bin/activate
pytest app/tests/ -v

# Frontend testleri
cd socialMedia_frontend
flutter test

# API manuel test
curl http://localhost:8000/
curl http://localhost:8000/docs
```

---

## 📁 Proje Yapısı Özeti

```
yzta_bootcamp_2026/
├── README.md                    # Bu dosya
├── SETUP_GUIDE.md              # Detaylı kurulum rehberi
├── socialMedia_backend/        # FastAPI Backend
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/routers/        # API endpoint'leri
│   │   ├── core/               # Config, DB, Email
│   │   ├── domain/schemas.py   # Pydantic modelleri
│   │   ├── repositories/       # Veritabanı erişimi
│   │   ├── services/           # AI, Storage, Auth
│   │   └── tests/              # Pytest testleri
│   ├── requirements.txt
│   └── migrate.py
├── socialMedia_frontend/       # Flutter Frontend
│   ├── lib/
│   │   ├── core/               # API, Theme, Router
│   │   ├── features/           # Feature modülleri
│   │   │   ├── auth/
│   │   │   ├── feed/
│   │   │   ├── wardrobe/
│   │   │   ├── ai_stylist/
│   │   │   ├── profile/
│   │   │   └── ...
│   │   └── main.dart
│   ├── pubspec.yaml
│   └── test/
└── docs/
    └── privacy_checklist.md
```

---

## 📝 Notlar

- **Ollama** ayrı bir terminalde `ollama serve` ile çalışmalıdır
- **İlk AI isteği** model RAM'e yüklendiği için 10-30 saniye sürebilir, sonraki istekler hızlıdır
- **Geliştirme modunda** backend `--reload` ile kod değişikliklerinde otomatik yenilenir
- **Veritabanı** SQLite (`dijital_gardrop.db`) dosya tabanlıdır, silip yeniden oluşturabilirsiniz
- **Detaylı kurulum** için `SETUP_GUIDE.md` dosyasına bakın

---

*Son güncelleme: 2026*  
*Proje: Dijital Gardrop - AI-Powered Social Fashion Platform*  
*YZTA Bootcamp 2026 - Takım 35*