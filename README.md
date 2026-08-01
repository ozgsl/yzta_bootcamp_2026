# Dijital Gardrop

**Yapay Zeka Destekli Moda & Sosyal Medya Platformu (Clean Architecture & VTON Entegrasyonu)**

> YZTA Bootcamp 2026 — Takım 35 Proje ve Geliştirme Raporu

### Proje Ekibi (Takım 35)
Projemiz, modern yazılım prensipleri ve yapay zeka entegrasyonlarıyla 4 kişilik bir ekip tarafından titizlikle tasarlanmış ve geliştirilmiştir:
- **Scrum Master & Branding**
- **Project Manager & AI Engineer (Yapay Zeka Mimarisi)**
- **Lead Developer (Temiz Mimari & Backend-Frontend Entegrasyonu)**
- **Marketing Researcher & Business Analyst (İş ve Strateji Analisti)**

Dijital Gardrop; kullanıcıların giysilerini akıllıca kataloglamalarına, profesyonel yapay zeka stilistinden gerçek zamanlı kombin önerileri almalarına, sanal giyinme kabininde (VTON) giysi denemelerine ve etkileşimli moda ağında paylaşım yapmalarına olanak tanıyan bir platformdur.

---

## İçindekiler
- [Mimari Devrim ve Clean Architecture](#mimari-devrim-ve-clean-architecture)
- [Teknoloji Yığınları (Tech Stack)](#teknoloji-yığınları-tech-stack)
- [Yapay Zeka ve AI Stilist Entegrasyonları](#yapay-zeka-ve-ai-stilist-entegrasyonları)
- [Veritabanı ve Güvenli Test Yönetimi](#veritabanı-ve-güvenli-test-yönetimi)
- [API Uç Noktaları ve Modüler Yapı](#api-uç-noktaları-ve-modüler-yapı)
- [Ağ, Bağlantı ve Cihaz Kurulma Korumaları](#ağ-bağlantısı-ve-cihaz-kurulum-korumaları)
- [Hızlı Giriş İçin Hazır Test Hesapları](#hızlı-giriş-için-hazır-test-hesapları)
- [Kurulum ve Çalıştırma Rehberi](#kurulum-ve-çalıştırma-rehberi)

---

## Mimari Devrim ve Clean Architecture
Projemiz, spagetileşmiş monolithic prototip aşamasından **Clean Architecture (Temiz Mimari)** ve **Katmanlı Tasarım (Layered Domain-Driven Architecture)** ilkelerine eksiksiz uyacak şekilde dönüştürülmüştür:

1. **Katmanlı Ayrışma (Router ➔ Service ➔ Repository ➔ Schema):**
   - **Router Katmanı (`app/api/routers/`):** Yalnızca HTTP isteklerini karşılayan ve DTO modellemelerini yöneten, veritabanından tamamen izole edilmiş API denetleyicileri.
   - **Servis Katmanı (`app/services/`):** Tüm AI pipeline entegrasyonu, bildirim işleyicileri, şifreleme ve iş mantığının (Business Logic) merkezi olarak yürütüldüğü kontrol merkezi.
   - **Repository Katmanı (`app/repositories/`):** Veritabanı sorgularının tam kalifiye SQLAlchemy modelleri ile işlendiği ve **N+1 sorgu problemlerine** karşı optimize edilmiş esnek veri geçişi katmanı.
2. **Entity ve DTO Ayırımı:** Pydantic (`app/domain/schemas.py`) şemaları ile SQLAlchemy ORM tablo varlıkları (`app/models/`) kati çizgilerle ayrılarak dışarıdan gelebilecek enjeksiyon ve bozuk veriler engellenmiştir.

---

## Teknoloji Yığınları (Tech Stack)

| Katman / Alan | Teknoloji / Kütüphane | Sürüm / Altyapı | Avantaj & Kullanım Amacı |
|---|---|---|---|
| **Mobil İstemci** | Flutter & Dart | Flutter 3.10+ / Dart 3.0+ | Cross-platform UI, yüksek performanslı esnek modüler rendering. |
| **Durum Yönetimi (State)** | Riverpod | 2.4.9 | Reaktif, güvenli, test edilebilir modern katmanlı durum denetimi. |
| **Önbellek & Depolama** | Cached Network Image & SharedPreferences | en güncel | Ağ verilerini koruyan ve eski oturum çizmelerini sıfırlayan çift mekanizmalı oturum denetimi. |
| **REST API Arka Uç** | FastAPI & Pydantic V2 | 0.110+ | Asenkron, Swagger dokümanı otomatik üreten ve veri doğrulayan modern Python servis çatı sistemi. |
| **Veritabanı** | PostgreSQL & Docker & Supabase | PostgreSQL 15+ / Alembic | Legacy SQLite yapısından profesyonel, ölçeklenebilir ve bağımsız tablo denetimli PostgreSQL evrimi. |
| **ORM & Migrasyon** | SQLAlchemy 2.0 & Alembic | 2.0+ | Modern tip tanımlı asenkron uyumlu ORM yapılandırması ve planlı migrasyon geçişleri. |
| **Yapay Zeka (Görsel Analiz)**| Moondream2 & FashionSigLIP | HuggingFace Zero-Shot CLIP / Ollama | Giysi tanıma, otomatik kıyafet rengi/stili etiketleme ve görsel resim caption tamamlama. |
| **Yapay Zeka (Sanal Deneme)**| VTON (Virtual Try-On - Fashn.ai) | Experimental VTON / Smart Fallback | Kullanıcının giysileri kendi görseli üzerinde sanal kabin ile deneme modülü. |

---

## Yapay Zeka ve AI Stilist Entegrasyonları
Platformumuz üç devrim niteliğinde yapay zeka modülü barındırır:

### 1. VTON (Sanal Giyim Deneme Kabini - Virtual Try-On)
- **Modül Path:** `app/api/routers/vton.py`
- Yüklenen veya gardıropta yer alan kıyafetler, kullanıcı modeli üzerinde `fashn.ai` görsel motoruyla sanki o an giyiliyormuş gibi sanal olarak giydirilerek dönüştürülür.
- 🛡️ **Akıllı Simülasyon (Mock) Koruması:** Geliştiricinin veya test eden bilgisayarın GPU'sunu tıkamamak ve sıfır API maliyeti sağlamak amacıyla; ortamda API Anahtarı bulunmasa bile **Mock Simülasyon Modu** otomatik devreye girerek milisek sürede profesyonel görsel çıktısı döndürür. Ağır dosya veya ek yazılım indirmeye hiç gerek kalmaz.

### 2. Moondream2 & FashionSigLIP (Görsel Tanıma & Otomatik Etiketleme)
- **Modül Path:** `app/services/fashion_classifier.py` & `app/services/ollama_caption_service.py`
- Gardırobuna yeni fotoğraf eklediğinde, kıyafetin t-shirt mü ceket mi olduğu, HSL/RGB temeli harmanlanmış rengi, mevsimi ve stil kurgusu sıfır-atış (Zero-Shot) FashionSigLIP modeli ile ayrıştırılır.
- LLaVA yerine entegre edilen hafif ve kesinlik şampiyonu **Moondream2** sayesinde görseller akıcı bir biçimde analiz edilir, çevredeki sunucular uykudaysa akıllı fallback modülüyle kırılmaz bir akış sunar.

### 3. Bağlam Farkındalıklı AI Stilist (LLaMA 3.2 & Akıllı Hafıza)
- **Modül Path:** `app/services/ollama_client.py` & `app/api/routers/wardrobe.py`
- AI stilist ile yazıştığınızda, sistem gardırobunuzdaki sadece **"Temiz (kullanılabilir)"** statüsündeki kıyafet listesini, günün tarihini ve oturum sohbet geçmişinizi otomatik bağlamlaşırarak ince bir paket halinde LLM'e taşır. Sonuç olarak: *"Dışarısı serin görünüyorsa, gardırobundaki temiz gri kazak ile siyah blazeri kombinleyebilirsin!"* tarzında hedeften şaşmayan şık öneriler kurgulanır.

---

## Veritabanı ve Güvenli Test Yönetimi
Eski sürümdeki tek dosya tabanlı kırılgan SQLite altyapısından vazgeçilip köklü bir veri devrimine gerilmiştir:
- **PostgreSQL Evrimi:** Veritabanı tamamen PostgreSQL temeline (Docker veya Supabase bulutu uyurlu) oturtulmuş, kimlik doğrulamalardan gardırop ilişkilerine kadar her tablo endeksli ve constraint destekli entegre edilmiştir.
- **Kritik Altın Kural (`TEST_DATABASE_URL`):** Projenin canlı (production) veya test ortamları birbirinden duvarlarla ayrılmıştır. Yasal güvenlik ve geliştirme kuralları gereği, test suite yazılımlarında **ASLA production veritabanına bağlanılamaz**. `app/core/config.py` bünyesinde bu izolasyon zırhı zorunlu parametrelerle mühürlenmiştir.

---

## API Uç Noktaları ve Modüler Yapı
FastAPI uygulamamız, Clean Architecture standartlarına yakışır derecede ayrık modüllerden (router gruplarından) oluşturulmuştur (`app/main.py`):

| Router Modülü | Uç Noktaları ve Yetenekler | Katman Yetkisi |
|---|---|---|
| **`auth.py`** | `POST /auth/login`, `POST /auth/register` | JWT Token Yönetimi & şifreli salt oturumları. |
| **`users.py`** | `GET /users/{id}`, `PUT /users/me`, `PUT /users/me/privacy` | UUID destekli korumalı ve esnek üye kimliği profilleme. |
| **`posts.py`** | `POST /posts`, `GET /posts/users/{uid}/posts`, `DELETE /posts/{id}` | Gönderi yükleme, kategori CHECK ilişki eşleştirmeleri. |
| **`likes.py` & `comments.py`** | `POST/DELETE /posts/{id}/like`, `POST/GET /posts/{id}/comments` | Gerçek zamanlı etkileşim yönetimi ve yorum ağaçları. |
| **`wardrobe.py`** | `POST /wardrobe/items`, `GET /wardrobe/items/{uid}`, `POST /wardrobe/chat` | Kıyafet listeleme, silme ve AI Stilist akıllı sohbet motoru. |
| **`vton.py`** | `POST /vton/tryon` | Sanal deneme (Virtual Try-On) entegrasyonu ve resim harmanlama. |
| **`captions.py`** | `POST /captions/suggest`, `POST /captions/upload` | Görsel yükleme haritası (`static/uploads/`) ve caption önerimi. |
| **`analytics.py` & `ai_export.py`** | `GET /analytics/stats`, `POST /export/ai` | Kullanıcı istatistiği analizleri ve AI veri haritası dökümü. |

---

## Ağ, Bağlantı ve Cihaz Kurulum Korumaları
Yerel PC, simülatör veya gerçek physical mobil cihaz testlerinde ortaya çıkabilen *Windows Güvenlik Duvarı Bloklama*, *İstek Zaman Aşımı (Timeout)* veya *Stale Session Error 500* engellerine karşı 3 aşamalı çelik güvenlik kalkanı kurulmuştur:

1. **Akıllı IP Adaptasyonu:** `app_config.dart` dosyası güncel ağ IP adresini direkt görecek şekilde uyarlandı.
2. **USB Port Tünellemesi (ADB Reverse):** Mobil cep telefonunun doğrudan kablo üzerinden ağ engeli yaşamadan bilgisayara bağlanabilmesi adına `adb reverse tcp:8000 tcp:8000` köprüsü entegre edildi. Telefonlar her koşulda 0.0.0.0:8000 üzerinden mermi gibi API iletişimine geçer.
3. **Eski Oturum Sökücü (Stale Session Cleaner):** SQLite döneminden kalma veya hafızaya tutunan eskinin sahte oturum stringleri (`"user-..."`), uygulama ilk uyanışında tespit edildiğinde temizlenir ve kullanıcı sorunsuz biçimde Giriş (Login) ekranına karşılanır.

---

## Hızlı Giriş İçin Hazır Test Hesapları
Jüri sunumu ve uygulama gezisi esnasında vakit kaybı yaşanmaması adına veritabanına hazır, şifreleri standardize edilmiş e-posta doğrulamasına (`gmail`, `hotmail`, `outlook` kurallarına uyan) sahip resmi test hesapları önceden eklenmiştir:

| Rol / Deney Hesabı | Geçerli E-Posta Adresi | Şifre | Durum |
|---|---|---|---|
| 👑 **Özge (Ana Hesap - Gmail)** | `ozge@gmail.com` | `123456` | Anında Girişe Hazır 🟢 |
| 👑 **Özge (Ana Hesap - Hotmail)** | `ozge@hotmail.com` | `123456` | Anında Girişe Hazır 🟢 |
| 👤 **Test Kullanıcı** | `test@gmail.com` | `123456` | Anında Girişe Hazır 🟢 |
| 💻 **Ahmet (Dev Hesap)** | `ahmet@gmail.com` | `123456` | Anında Girişe Hazır 🟢 |

---

## Kurulum ve Çalıştırma Rehberi

### 1. Arka Uç Sunucusunu (FastAPI) Uyandırın
```bash
# Terminal 1 - Backend Dizinine Geç
cd socialMedia_backend

# Bağımlılıkları kontrol et veya kur
pip install -r requirements.txt

# Sunucuyu IP kısıtlamasız (0.0.0.0) başlat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Sunucu o an uyanır. Tarayabilmeniz için **Swagger UI API Dokümani:** `http://localhost:8000/docs`

### 2. Mobil Çift Bağlantı (USB Tüneli) ve Flutter İstemcisi
Telefonu PC'ye takın ve tek komutla engelsiz, çakılmasız direkt uygulamanın içine inin:
```bash
# Terminal 2 - Mobil Köprü ve Çalıştırma
cd socialMedia_frontend

# (Opsiyonel ama önerilir): Telefonun ağa takılmadan USB üzerinden PC'yi okumasını sağla:
adb reverse tcp:8000 tcp:8000

# Uygulama Paketleme ve Fiziksel Cihazda Açış
flutter run -d <cihaz_idi> # veya sadece "flutter run"
```

---

*Proje Raporu: YZTA Bootcamp 2026 - Takım 35 | Profesyonel Sistem Tasarımı ve Katmanlı Evrim.*  
*Tüm Hakları ve Kod Gelişim Prensip Hakları Takım 35'e Aittir.*