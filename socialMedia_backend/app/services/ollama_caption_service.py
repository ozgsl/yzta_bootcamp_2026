"""
AI Caption Servisi — Tamamen Yerel, Ollama tabanlı. Harici API yok.
Gemini veya herhangi bir harici API KULLANILMAZ.

Pipeline:
  1. llava  (görsel model)  → Kıyafetleri JSON listesi olarak tespit eder
  2. llama3.2 (metin model) → Tespiti alıp kombinin neden seçildiğini açıklar

Endpoints:
  POST /captions/suggest       → Kısa caption üretir (mevcut, korundu)
  POST /captions/upload        → Resim yükler, URL + FashionSigLIP analizi döner
  POST /captions/analyze-item  → Tek kıyafet analizi (mevcut, korundu)
  POST /captions/outfit-story  → LLaVA tespit + Ollama hikaye (YENİ)
"""
from __future__ import annotations

import base64
import hashlib
import os
import uuid
import httpx
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional

from pydantic import BaseModel
from app.domain.schemas import CaptionRequest, MessageResponse
from app.services.fashion_classifier import classifier as fashion_classifier

router = APIRouter()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Görsel model: moondream (~1.7GB int4) — M2 MacBook Air optimized
# Alternatif: "moondream:1.8b-fp16" (~3.5GB, daha iyi kalite)
# Ollama ile küme: ollama pull moondream
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "moondream")
# Metin modeli: llama3.2 — Türkçe hikaye/caption üretimi
OLLAMA_TEXT_MODEL   = os.getenv("OLLAMA_MODEL",        "llama3.2")

# Resim kayıt dizini
UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("SERVER_PORT", "8000")


# ────────────────────────────────────────────────────────
# Yardımcı: Görseli base64'e çevir + Güvenli JSON parse + Normalize/Dedup
# ────────────────────────────────────────────────────────

_VALID_ITEM_FIELDS = {"kategori", "tip", "renk", "desen", "tarz", "malzeme_tahmini", "confidence"}
_TARZ_VALS        = {"casual", "spor", "sik", "resmi", "vintage"}


def _safe_parse_json(raw: str):
    """
    Ham metin içinden JSON array veya object çıkarır.
    Model bazen array yerine object, bazen yarım JSON döndürür.
    Dönüş: (parsed_value, 'object'|'array'|None)
    """
    import json as _json
    # Markdown temizle
    for marker in ["```json", "```"]:
        if marker in raw:
            parts = raw.split(marker)
            if len(parts) > 1:
                raw = parts[1].split("```")[0].strip()
            break
    # En uzun geçerli JSON'u önce array sonra object olarak dene
    candidates = []
    sa, ea = raw.find("["), raw.rfind("]") + 1
    so, eo = raw.find("{"), raw.rfind("}") + 1
    if sa != -1 and ea > sa:
        candidates.append(("array", raw[sa:ea]))
    if so != -1 and eo > so:
        candidates.append(("object", raw[so:eo]))
    best = None
    for kind, chunk in candidates:
        try:
            val = _json.loads(chunk)
            if best is None or len(chunk) > len(best[2]):
                best = (val, kind, chunk)
        except _json.JSONDecodeError:
            pass
    if best:
        return best[0], best[1]
    return None, None


def _normalize_item(item: dict) -> dict:
    """Model çıktısındaki hatalı alan adlarını düzeltir, eksikleri varsayılanla doldurur."""
    cleaned = {k: v for k, v in item.items() if k in _VALID_ITEM_FIELDS}
    cleaned.setdefault("kategori", "ust giyim")
    cleaned.setdefault("tip", "")
    cleaned.setdefault("renk", "")
    cleaned.setdefault("desen", "duz")
    cleaned.setdefault("tarz", "casual")
    cleaned.setdefault("malzeme_tahmini", None)
    try:
        cleaned["confidence"] = float(item.get("confidence", 0.7))
    except (TypeError, ValueError):
        cleaned["confidence"] = 0.7
    # Model tarz değerini yanlış alana yazmışsa kurtar
    for k in item:
        if k in _TARZ_VALS and not cleaned.get("tarz"):
            cleaned["tarz"] = k
    # Legacy uyumluluk
    cleaned["tur"]  = cleaned.get("tip", "")
    cleaned["stil"] = cleaned.get("tarz", "")
    return cleaned


def _deduplicate_items(items: list) -> list:
    """Aynı (tip, renk, desen) kombinasyonunu tekrar ekleme."""
    seen, result = set(), []
    for item in items:
        key = hashlib.md5(
            f"{item.get('tip','').lower()}|{item.get('renk','').lower()}|{item.get('desen','')}"
            .encode()
        ).hexdigest()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


# ────────────────────────────────────────────────────────
# Yardımcı: Görseli base64'e çevir
# ────────────────────────────────────────────────────────

def _image_to_base64(image_url: Optional[str]) -> Optional[str]:
    """
    Görsel URL'sini alır:
    - Yerel static/uploads/ dosyasıysa diskten okur
    - Harici URL ise indirir
    None döner başarısız olursa.
    """
    if not image_url:
        return None

    # Yerel dosya
    if "static/uploads/" in image_url:
        filename = image_url.split("static/uploads/")[-1].split("?")[0]
        local_path = UPLOADS_DIR / filename
        if local_path.exists():
            return base64.b64encode(local_path.read_bytes()).decode()
        return None

    # Harici URL → indir
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(image_url)
            resp.raise_for_status()
            return base64.b64encode(resp.content).decode()
    except Exception as e:
        print(f"[Vision] Image download error ({image_url}): {e}")
        return None


# ─────────────────────────────────────────────────────────────
# 1) MOONDREAM2 — Görsel anlayan yerel model (Ollama üzerinden)
# ─────────────────────────────────────────────────────────────

def _caption_with_moondream(
    image_b64: Optional[str],
    outfit_desc: str,
    style_hint: str = "",
    fashion_analysis: Optional[dict] = None,
) -> Optional[str]:
    """
    Moondream2 (Ollama) ile görsel analizi yapar ve Türkçe caption üretir.
    FashionSigLIP analiz sonuçları varsa prompt'a eklenir.
    Model kurulu değilse None döner.
    """
    if not image_b64:
        return None

    # Moondream için kısa ve net prompt — model kısa sorulara daha iyi yanıt veriyor
    context_parts = []
    if outfit_desc and outfit_desc not in ("Kombin", "diger: bilinmiyor"):
        context_parts.append(f"Outfit: {outfit_desc}.")
    if style_hint:
        context_parts.append(f"Style: {style_hint}.")
    if fashion_analysis:
        context_parts.append(
            f"Detected: {fashion_analysis.get('tur', '')}, "
            f"{fashion_analysis.get('renk', '')}, "
            f"{fashion_analysis.get('stil_etiketi', '')}."
        )
    context = " ".join(context_parts)

    prompt = (
        f"Write a short, catchy Turkish social media caption for this outfit photo. "
        f"{context} "
        f"Max 200 characters. Use emojis. Add hashtags like #moda #ootd #kombin. "
        f"Return ONLY the caption text."
    )

    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "keep_alive": "10m",
        "options": {"temperature": 0.7, "num_predict": 100},
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            if resp.status_code == 404:
                print(f"[Moondream] Model '{OLLAMA_VISION_MODEL}' kurulu degil. 'ollama pull moondream' calistir.")
                return None
            resp.raise_for_status()
            result = resp.json().get("response", "").strip()
            return result[:280] if result else None
    except httpx.ConnectError:
        print("[Moondream] Ollama baglanti hatasi — ollama serve calisiyor mu?")
        return None
    except Exception as e:
        print(f"[Moondream] Caption hatasi: {e}")
        return None


# ───────────────────────────────────────────────────────────────────────────
# 3) MOONDREAM2 KİYAFET TESPİTİ — Pipeline Adım 1
#    Çıktı şeması (genisletilmis): kategori/tip/renk/desen/tarz/malzeme_tahmini/confidence
# ───────────────────────────────────────────────────────────────────────────

def _ask_moondream_sync(image_b64: str, question: str, max_tokens: int = 15) -> str:
    """
    Moondream'e tek basit soru sorar, kısa yanıt alır (sync versiyon).
    Multi-query yaklaşımında her özellik için ayrı çağrı yapılır.
    """
    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": question,
        "images": [image_b64],
        "stream": False,
        "keep_alive": "10m",
        "options": {"temperature": 0.0, "num_predict": max_tokens},
    }
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "").strip().lower()
    except Exception:
        return ""


_KATEGORI_MAP = {
    "tisort": "ust giyim", "gomlek": "ust giyim", "kazak": "ust giyim",
    "hirka": "ust giyim", "bluz": "ust giyim", "atlet": "ust giyim",
    # ingilizce fallback
    "shirt": "ust giyim", "t-shirt": "ust giyim", "tshirt": "ust giyim",
    "blouse": "ust giyim", "sweater": "ust giyim", "hoodie": "ust giyim",
    "top": "ust giyim",
    "pantolon": "alt giyim", "etek": "alt giyim", "sort": "alt giyim",
    "tayt": "alt giyim", "jean": "alt giyim",
    "pants": "alt giyim", "jeans": "alt giyim", "skirt": "alt giyim",
    "leggings": "alt giyim", "shorts": "alt giyim", "trousers": "alt giyim",
    "mont": "dis giyim", "kaban": "dis giyim", "ceket": "dis giyim",
    "trencot": "dis giyim", "yelek": "dis giyim",
    "jacket": "dis giyim", "coat": "dis giyim", "blazer": "dis giyim",
    "vest": "dis giyim",
    "bot": "ayakkabi", "ayakkabi": "ayakkabi", "sandalet": "ayakkabi",
    "shoes": "ayakkabi", "sneakers": "ayakkabi", "boots": "ayakkabi",
    "sandals": "ayakkabi", "heels": "ayakkabi",
    "canta": "aksesuar", "kemer": "aksesuar", "sapka": "aksesuar",
    "bag": "aksesuar", "hat": "aksesuar", "scarf": "aksesuar",
    "belt": "aksesuar", "gloves": "aksesuar",
}

# İngilizce kıyafet → Türkçe kıyafet
_TIP_MAP = {
    "shirt": "gomlek", "t-shirt": "tisort", "tshirt": "tisort",
    "top": "tisort", "blouse": "bluz", "sweater": "kazak", "hoodie": "hirka",
    "pants": "pantolon", "jeans": "pantolon", "trousers": "pantolon",
    "skirt": "etek", "leggings": "tayt", "shorts": "sort",
    "jacket": "ceket", "coat": "mont", "blazer": "ceket",
    "vest": "yelek", "dress": "elbise", "suit": "takim elbise",
    "shoes": "ayakkabi", "sneakers": "spor ayakkabi", "boots": "bot",
    "sandals": "sandalet", "heels": "topuklu",
    "bag": "canta", "hat": "sapka", "scarf": "atki",
    "belt": "kemer", "gloves": "eldiven",
}

# İngilizce renk → Türkçe renk
_RENK_MAP = {
    "white": "beyaz", "black": "siyah", "gray": "gri", "grey": "gri",
    "navy": "lacivert", "blue": "mavi", "red": "kirmizi", "green": "yesil",
    "yellow": "sari", "orange": "turuncu", "pink": "pembe", "purple": "mor",
    "brown": "kahverengi", "beige": "bej", "cream": "krem",
    "light": "acik", "dark": "koyu",
}
_VALID_RENKLER = ["beyaz","siyah","gri","lacivert","mavi","kirmizi","yesil",
                   "sari","turuncu","pembe","mor","kahverengi","bej","krem"]
_VALID_TARZ    = ["casual","spor","sik","resmi","vintage"]
_VALID_DESEN   = ["duz","cizgili","kareli","desenli","baskili"]
_VALID_DESEN_EN = ["solid","stripe","check","pattern","print"]
_DESEN_EN_MAP  = {"solid":"duz","stripe":"cizgili","stripes":"cizgili",
                   "check":"kareli","checkered":"kareli","pattern":"desenli",
                   "print":"baskili","printed":"baskili"}


def _norm(raw: str, valid: list, default: str) -> str:
    """Ham kısa yanıttan geçerli değer çıkarır."""
    raw = raw.lower().strip().rstrip(".,;:!")
    for v in valid:
        if v in raw:
            return v
    return default


def _parse_description_to_items(description: str) -> list:
    """
    Moondream'in serbest metin açıklamasını parse ederek
    yapılandırılmış kıyafet listesi çıkarır.

    Örn giriş: "The man is wearing a light blue polo shirt with black pants and black shoes."
    Örn çıkış: [
      {"tip":"gomlek","renk":"mavi","tarz":"casual","desen":"duz","kategori":"ust giyim",...},
      {"tip":"pantolon","renk":"siyah",...},
      {"tip":"ayakkabi","renk":"siyah",...},
    ]
    """
    text = description.lower()
    words = set(text.split())

    # Tarz tespiti
    _TARZ_EN = {"casual":"casual","formal":"resmi","sporty":"spor","elegant":"sik",
                 "sport":"spor","chic":"sik","vintage":"vintage","business":"resmi"}
    tarz = "casual"
    for en, tr in _TARZ_EN.items():
        if en in text:
            tarz = tr
            break

    # Desen tespiti
    desen = "duz"
    for en, tr in _DESEN_EN_MAP.items():
        if en in text:
            desen = tr
            break

    # Kıyafet öğesi tanıma — renk+tip çiftleri
    items_raw = []
    _COLORS = {
        "white":"beyaz","black":"siyah","gray":"gri","grey":"gri",
        "navy":"lacivert","blue":"mavi","light blue":"mavi","dark blue":"lacivert",
        "red":"kirmizi","green":"yesil","yellow":"sari","orange":"turuncu",
        "pink":"pembe","purple":"mor","brown":"kahverengi","beige":"bej",
        "cream":"krem","khaki":"bej","olive":"yesil","maroon":"bordo",
    }
    _GARMENTS_EN = [
        ("polo shirt","gomlek"),("polo","gomlek"),("shirt","gomlek"),
        ("t-shirt","tisort"),("tshirt","tisort"),("top","tisort"),
        ("blouse","bluz"),("sweater","kazak"),("hoodie","hirka"),
        ("sweatshirt","hirka"),("cardigan","hirka"),("vest","yelek"),
        ("dress","elbise"),("gown","elbise"),("suit","takim"),
        ("blazer","ceket"),("jacket","ceket"),("coat","mont"),
        ("pants","pantolon"),("trousers","pantolon"),("jeans","pantolon"),
        ("skirt","etek"),("leggings","tayt"),("shorts","sort"),
        ("shoes","ayakkabi"),("sneakers","spor ayakkabi"),("boots","bot"),
        ("sandals","sandalet"),("heels","topuklu"),("loafers","ayakkabi"),
        ("bag","canta"),("backpack","canta"),("hat","sapka"),
        ("scarf","atki"),("belt","kemer"),
    ]

    # Her garment için metinde ara
    for en_garment, tr_garment in _GARMENTS_EN:
        if en_garment not in text:
            continue

        # Kıyafetin önündeki 3 kelimede renk ara
        idx = text.find(en_garment)
        prefix = text[max(0, idx-30):idx]

        renk = "belirsiz"
        # Önce 2-kelime renk (light blue, dark blue)
        for color_en, color_tr in _COLORS.items():
            if color_en in prefix:
                renk = color_tr
                break

        kategori = _KATEGORI_MAP.get(en_garment, _KATEGORI_MAP.get(tr_garment, "ust giyim"))

        items_raw.append({
            "kategori": kategori,
            "tip": tr_garment,
            "renk": renk,
            "desen": desen,
            "tarz": tarz,
            "malzeme_tahmini": None,
            "confidence": 0.85,
            "tur": tr_garment,
            "stil": tarz,
        })

    # Hiç bulunamadıysa genel bir item üret
    if not items_raw:
        # En azından genel renk ve tarz bul
        genel_renk = "belirsiz"
        for color_en, color_tr in _COLORS.items():
            if color_en in text:
                genel_renk = color_tr
                break
        items_raw.append({
            "kategori": "ust giyim",
            "tip": "kiyafet",
            "renk": genel_renk,
            "desen": desen,
            "tarz": tarz,
            "malzeme_tahmini": None,
            "confidence": 0.5,
            "tur": "kiyafet",
            "stil": tarz,
        })

    return _deduplicate_items(items_raw)


def _detect_outfit_items_with_moondream(image_b64: str) -> list:
    """
    Moondream2 ile kıyafet analizi — Describe → Parse yaklaşımı.

    Kanıtlanan çalışma şekli:
    1. Moondream'e "Describe the clothing" sorusu sorulur (serbest metin → güvenilir)
    2. Gelen İngilizce metin Python keyword matching ile parse edilir
    3. Yapılandırılmış kıyafet listesi döner

    Q&A / JSON üretme yaklaşımları Ollama'nın context caching'i nedeniyle
    boş yanıt veriyor; bu yaklaşım her zaman çalışır.
    """
    try:
        with httpx.Client(timeout=10.0) as _test:
            _test.get(f"{OLLAMA_BASE_URL}/api/tags").raise_for_status()
    except Exception:
        print("[Moondream-Detect] Ollama baglanti hatasi.")
        return []

    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": (
            "Describe the clothing worn by the person in this photo. "
            "Include every item: shirt, pants, shoes, jacket, accessories. "
            "Mention the color of each item and the overall style (casual/formal/sporty)."
        ),
        "images": [image_b64],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 150},
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            resp.raise_for_status()
            description = resp.json().get("response", "").strip()

        if not description:
            print("[Moondream-Detect] Bos yanit.")
            return []

        print(f"[Moondream-Detect] Aciklama: {description[:120]}...")
        items = _parse_description_to_items(description)
        print(f"[Moondream-Detect] {len(items)} kiyafet parse edildi: "
              f"{[i['tip']+'/'+i['renk'] for i in items]}")
        return items

    except httpx.ConnectError:
        print("[Moondream-Detect] Ollama baglanti hatasi.")
        return []
    except Exception as e:
        print(f"[Moondream-Detect] Hata: {e}")
        return []



# ─────────────────────────────────────────────────────────────────────────────
# 4) OLLAMA ile KOMBİN HİKAYESİ — Yeni Pipeline Adım 2
# ─────────────────────────────────────────────────────────────────────────────

def _generate_outfit_story_with_ollama(
    detected_items: list,
    style_hint: str = "",
    fashion_analysis: Optional[dict] = None,
) -> str:
    """
    Tespit edilen kıyafet listesini alır ve kombini açıklayan Türkçe metin üretir.
    Sade metin formatı — llama3.2 markdown/bold syntax'ını iyi işlemiyor.
    Hedef: 400-700 karakter.
    """
    if not detected_items:
        return ""

    # Kıyafet listesi — kısa ve net
    items_text = ", ".join(
        f"{item['tur']}"
        + (f" ({item['renk']}" if item.get('renk') else "")
        + (f", {item['stil']} stil" if item.get('stil') else "")
        + (")" if item.get('renk') or item.get('stil') else "")
        for item in detected_items
    )

    # Ek bağlam
    extra = ""
    if style_hint:
        extra += f" Stil tercihi: {style_hint}."
    if fashion_analysis and fashion_analysis.get("stil_etiketi"):
        extra += f" Genel stil: {fashion_analysis['stil_etiketi']}."
    if fashion_analysis and fashion_analysis.get("mevsim"):
        extra += f" Mevsim: {fashion_analysis['mevsim']}."

    prompt = (
        f"Sen bir Turk moda editörüsün.{extra}\n"
        f"Bu kombini analiz et: {items_text}\n\n"
        "1. Her parca icin tek cumle yaz: ne oldugu ve neden bu kombinle uyumlu oldugu.\n"
        "2. Renk uyumu ve stil butunlugu hakkinda 2 cumle yaz.\n"
        "3. 5 hashtag ekle (#moda #ootd #kombin gibi).\n"
        "Sadece Turkce yaz. Toplam 400-700 karakter. Markdown veya ** kullanma."
    )

    try:
        with httpx.Client(timeout=75.0) as client:
            resp = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_TEXT_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "10m",  # Model 10 dakika belleğinde kalır
                    "options": {
                        "temperature": 0.65,
                        "num_predict": 600,
                    },
                },
            )
            resp.raise_for_status()
            story = resp.json().get("response", "").strip()
            return story[:1000] if story else ""
    except httpx.ConnectError:
        print("[Ollama-Story] Ollama bağlantı hatası.")
        return ""
    except Exception as e:
        print(f"[Ollama-Story] Hata: {e}")
        return ""


# ─────────────────────────────────────────────────────────
# 2) OLLAMA LLAMA3.2 — Metin fallback
# ─────────────────────────────────────────────────────────

def _caption_text_only(
    outfit_desc: str,
    style_hint: str = "",
    fashion_analysis: Optional[dict] = None,
) -> str:
    """llama3.2 ile metin (+ isteğe bağlı FashionSigLIP analizi) bilgisine göre caption üretir."""
    prompt = (
        f"Şu kombin için kısa ve çekici bir sosyal medya caption'ı yaz "
        f"(Türkçe, max 200 karakter, emoji kullan, #moda #ootd #style gibi hashtag ekle):\n"
        f"Kombin: {outfit_desc}\n"
    )
    if style_hint:
        prompt += f"Stil: {style_hint}\n"
    if fashion_analysis:
        prompt += (
            f"Kıyafet türü: {fashion_analysis.get('tur', '')}\n"
            f"Renk: {fashion_analysis.get('renk', '')}\n"
            f"Stil etiketi: {fashion_analysis.get('stil_etiketi', '')}\n"
        )
    prompt += "Sadece caption'ı yaz, başka açıklama ekleme."

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_TEXT_MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "").strip()[:250]
    except httpx.ConnectError:
        print("[llama3.2] Ollama connection error.")
        return ""
    except Exception as e:
        print(f"[llama3.2] Error: {e}")
        return ""


# ─────────────────────────────────────────────────────────
# ENDPOINT: POST /captions/suggest
# ─────────────────────────────────────────────────────────

class CaptionRequestExtended(CaptionRequest):
    """
    CaptionRequest'i genişletir: FashionSigLIP analiz sonuçlarını kabul eder.
    /captions/upload'dan dönen ai_analysis dict'ini buraya iletebilirsiniz.
    """
    ai_analysis: Optional[dict] = None   # FashionSigLIP sonucu (opsiyonel)


@router.post("/suggest", response_model=MessageResponse)
async def suggest_caption(req: CaptionRequestExtended):
    """
    Kombin görseli + bilgilerinden Türkçe AI caption üretir.

    Öncelik sırası (hepsi yerel):
      1. FashionSigLIP ile görsel analizi (eğer model yüklüyse ve görsel varsa)
      2. llava ile görsel analizi (Ollama)
      3. llama3.2 metin fallback
      4. Statik fallback

    FashionSigLIP sonuçları her aşamadaki prompt'a eklenerek kalite artırılır.
    """
    items_desc = ", ".join(
        [f"{item.get('category', 'parça')}: {item.get('name', item.get('tur', 'bilinmiyor'))}"
         for item in req.outfit_items]
    ) if req.outfit_items else "Moda kombini"

    style_hint = req.style_hint or ""
    image_url  = req.image_url

    # --- FashionSigLIP analizi ---
    fashion_analysis: Optional[dict] = req.ai_analysis  # Client'tan gelebilir
    if not fashion_analysis and image_url and fashion_classifier.is_ready:
        try:
            image_b64_for_fashion = _image_to_base64(image_url)
            if image_b64_for_fashion:
                result = fashion_classifier.classify_image(image_b64=image_b64_for_fashion)
                if result.get("success"):
                    fashion_analysis = result
        except Exception as e:
            print(f"[FashionSigLIP] Suggest analysis error: {e}")

    caption: Optional[str] = None

    # 1. Görsel varsa Moondream2 ile analiz et
    if image_url:
        image_b64 = _image_to_base64(image_url)
        caption = _caption_with_moondream(image_b64, items_desc, style_hint, fashion_analysis)

    # 2. Sadece metin ile dene (Moondream yoksa veya görsel yoksa)
    if not caption:
        caption = _caption_text_only(items_desc, style_hint, fashion_analysis)

    # 3. Statik fallback
    if not caption:
        caption = f"✨ Harika bir kombin! 🔥 #moda #style #ootd #fashion"

    return MessageResponse(
        success=True,
        message="Caption önerisi üretildi",
        data={
            "caption": caption,
            "fashion_analysis": fashion_analysis,  # Analiz sonucunu da dönelim
        },
    )


# ─────────────────────────────────────────────────────────
# ENDPOINT: POST /captions/upload
# ─────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINT: POST /captions/outfit-story  (YENİ)
# ─────────────────────────────────────────────────────────────────────────────

class OutfitStoryRequest(BaseModel):
    image_url: Optional[str] = None
    image_b64: Optional[str] = None
    style_hint: str = ""
    ai_analysis: Optional[dict] = None  # FashionSigLIP sonucu (opsiyonel)


@router.post("/outfit-story")
async def generate_outfit_story(req: OutfitStoryRequest):
    """
    Moondream2 + llama3.2 pipeline:
    - FashionSigLIP + Moondream PARALEL çalışır (süre yarıya iner)
    - Moondream JSON başarısız olursa FashionSigLIP verisiyle hikaye yazılır
    """
    import asyncio

    # Görseli base64'e dönüştür
    image_b64 = req.image_b64
    if not image_b64 and req.image_url:
        image_b64 = _image_to_base64(req.image_url)

    if not image_b64:
        raise HTTPException(
            status_code=400,
            detail="Lütfen image_url veya image_b64 sağlayın."
        )

    loop = asyncio.get_event_loop()

    # ──── Moondream ve FashionSigLIP PARALEL çalıştır ──────────────────
    async def run_moondream():
        return await loop.run_in_executor(None, _detect_outfit_items_with_moondream, image_b64)

    async def run_fashion_siglip():
        if req.ai_analysis:
            return req.ai_analysis
        if not fashion_classifier.is_ready:
            return None
        try:
            result = await loop.run_in_executor(
                None, fashion_classifier.classify_image, None, image_b64
            )
            return result if result.get("success") else None
        except Exception as e:
            print(f"[FashionSigLIP] Hata: {e}")
            return None

    # Her ikisini paralel başlat
    moondream_task = asyncio.create_task(run_moondream())
    siglip_task = asyncio.create_task(run_fashion_siglip())
    detected_items, fashion_analysis = await asyncio.gather(moondream_task, siglip_task)
    # ─────────────────────────────────────────────────────────────

    # Moondream başarısız olduysa FashionSigLIP verisinden item listesi üret
    if not detected_items and fashion_analysis:
        detected_items = [{
            "kategori": "ust giyim",
            "tip": fashion_analysis.get("tur", "kiyafet"),
            "tur": fashion_analysis.get("tur", "kiyafet"),
            "renk": fashion_analysis.get("renk", ""),
            "desen": "duz",
            "tarz": fashion_analysis.get("stil_etiketi", ""),
            "stil": fashion_analysis.get("stil_etiketi", ""),
            "malzeme_tahmini": None,
            "confidence": float(fashion_analysis.get("confidence", 0.7)),
        }]
        print("[Pipeline] Moondream JSON parse edilemedi, FashionSigLIP verisi kullaniliyor.")

    # Ollama ile kombin hikayesi
    outfit_story = await loop.run_in_executor(
        None,
        lambda: _generate_outfit_story_with_ollama(
            detected_items,
            req.style_hint,
            fashion_analysis,
        ),
    )

    # Son fallback: statik metin
    if not outfit_story:
        outfit_story = (
            "Sik ve orijinal bir kombin! Kiyafet kombinasyonunuz renk uyumu "
            "ve stil butunlugu acisindan cok basarili. "
            "#moda #ootd #style #kombin #fashion"
        )

    return {
        "detected_items": detected_items,
        "outfit_story": outfit_story,
        "fashion_analysis": fashion_analysis,
    }


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Resim yükler, erişilebilir URL döndürür.
    Yükleme sonrasında FashionSigLIP ile otomatik kıyafet analizi yapar.
    """
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
    ext = Path(file.filename or "img.jpg").suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail="Sadece jpg, png, webp, heic desteklenir.")

    filename = f"{uuid.uuid4()}{ext}"
    dest = UPLOADS_DIR / filename
    content = await file.read()
    dest.write_bytes(content)

    url = f"http://{SERVER_HOST}:{SERVER_PORT}/static/uploads/{filename}"

    # FashionSigLIP ile otomatik analiz
    ai_analysis: Optional[dict] = None
    if fashion_classifier.is_ready:
        try:
            result = fashion_classifier.classify_image(image_path=dest)
            if result.get("success"):
                ai_analysis = {
                    "tur": result["tur"],
                    "renk": result["renk"],
                    "stil_etiketi": result["stil_etiketi"],
                    "mevsim": result["mevsim"],
                    "post_category": result["post_category"],
                    "confidence": result["confidence"],
                    "alternatifler": result.get("alternatifler", []),
                }
        except Exception as e:
            print(f"[FashionSigLIP] Upload analysis error: {e}")

    return {"url": url, "filename": filename, "ai_analysis": ai_analysis}

# -----------------------------------------------------------------------------
# ENDPOINT: POST /captions/analyze-item
# -----------------------------------------------------------------------------
class AnalyzeItemRequest(BaseModel):
    image_url: Optional[str] = None
    image_b64: Optional[str] = None

@router.post("/analyze-item")
async def analyze_item(req: AnalyzeItemRequest):
    """
    Moondream2 multi-query ile tek kıyafet analizi.
    JSON üretmek yerine 4 basit soru sorulur, sonuçlar birleştirilir.
    """
    import asyncio as _asyncio
    image_b64 = req.image_b64
    if not image_b64 and req.image_url:
        image_b64 = _image_to_base64(req.image_url)
    if not image_b64:
        raise HTTPException(status_code=400, detail="Lutfen image_url veya image_b64 saglayin.")

    try:
        loop = _asyncio.get_event_loop()
        # _detect_outfit_items_with_moondream zaten multi-query yapıyor, onu kullan
        items = await loop.run_in_executor(
            None, _detect_outfit_items_with_moondream, image_b64
        )
        if items:
            return {
                "success": True,
                "data": items[0],
                "schema_version": "moondream2-multiquery",
            }
        raise ValueError("Moondream tespiti bos dondu.")
    except Exception as e:
        return {
            "success": False,
            "message": f"Moondream analizi basarisiz: {str(e)}",
            "data": {
                "kategori": "", "tip": "", "renk": "",
                "desen": "", "tarz": "", "malzeme_tahmini": None,
                "confidence": 0.0, "tur": ""
            },
        }

