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
# Görsel model: llava (7b, ~4.7GB) — M2 MacBook Air ile uyumlu
# Yükseltme: llava:13b (~8GB) daha iyi tespit, ancak 16GB+ RAM gerektirir
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")
# Metin modeli: llama3.2:3b (~2GB) — Hızlı ve hafif
# Yükseltme: llama3.1:8b daha zengin açıklama, ancak ~5GB RAM gerektirir
OLLAMA_TEXT_MODEL   = os.getenv("OLLAMA_MODEL",        "llama3.2")

# Resim kayıt dizini
UPLOADS_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = os.getenv("SERVER_PORT", "8000")


# ─────────────────────────────────────────────────────────
# Yardımcı: Görseli base64'e çevir
# ─────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────
# 1) OLLAMA LLAVA — Görsel anlayan yerel model
# ─────────────────────────────────────────────────────────

def _caption_with_llava(
    image_b64: Optional[str],
    outfit_desc: str,
    style_hint: str = "",
    fashion_analysis: Optional[dict] = None,
) -> Optional[str]:
    """
    Ollama llava modeli ile görsel analizi yapar.
    FashionSigLIP analiz sonuçları varsa prompt'a eklenir — çok daha isabetli caption üretilir.
    llava kurulu değilse None döner.
    """
    if not image_b64:
        return None  # Görsel yoksa llava'ya gerek yok, metin fallback'e geç

    # Görsel analizi için zenginleştirilmiş prompt
    prompt_parts = [
        "Sen bir moda uzmanısın. Bu kıyafet/moda fotoğrafını dikkatlice incele.",
        "Görseldeki kıyafetleri, renkleri ve stili değerlendirerek",
        "kısa, özgün ve çekici bir Türkçe sosyal medya caption'ı yaz.",
        "Maksimum 250 karakter. Emoji kullan. Hashtag ekle (#moda #ootd #style #kombin gibi).",
    ]
    if outfit_desc and outfit_desc not in ("Kombin", "diğer: bilinmiyor"):
        prompt_parts.append(f"Kombinde şunlar var: {outfit_desc}.")
    if style_hint:
        prompt_parts.append(f"Stil tercihi: {style_hint}.")
    if fashion_analysis:
        prompt_parts.append(
            f"AI tespiti: '{fashion_analysis.get('tur', '')}', "
            f"renk '{fashion_analysis.get('renk', '')}', "
            f"stil '{fashion_analysis.get('stil_etiketi', '')}'."
        )
    prompt_parts.append("Sadece caption metnini yaz. Açıklama, not veya başlık ekleme.")
    prompt = " ".join(prompt_parts)

    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            if resp.status_code == 404:
                print(f"[llava] Model '{OLLAMA_VISION_MODEL}' kurulu değil. 'ollama pull llava' çalıştır.")
                return None
            resp.raise_for_status()
            result = resp.json().get("response", "").strip()
            return result[:280] if result else None
    except httpx.ConnectError:
        print("[llava] Ollama connection error - is ollama serve running?")
        return None
    except Exception as e:
        print(f"[llava] Error: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 3) LLaVA İLE ÇOKLU KIYAFet TESPİTİ — Yeni Pipeline Adım 1
# ─────────────────────────────────────────────────────────────────────────────

def _detect_outfit_items_with_llava(image_b64: str) -> list:
    """
    LLaVA vision modeli ile görseldeki tüm kıyafetleri tespit eder.
    İngilizce prompt kullanılıyor — llava 7b İngilizce komutlarda daha tutarlı.
    """
    import json as _json

    # İngilizce prompt: llava 7b İngilizce'de daha iyi JSON üretiyor
    prompt = (
        "List ALL clothing items and accessories visible in this photo. "
        "For each item output ONLY a JSON array. "
        "Fields: tur (Turkish clothing name, e.g. blazer/pantolon/gomlek/elbise/bot/canta), "
        "renk (Turkish color name), kumas (fabric if visible, else empty), stil (resmi/gundelik/spor/sik). "
        "Example: [{\"tur\":\"blazer\",\"renk\":\"lacivert\",\"kumas\":\"yun\",\"stil\":\"resmi\"}] "
        "Output ONLY the JSON array. No explanation, no markdown."
    )

    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
        "keep_alive": "10m",  # Model 10 dakika belleğinde kalır
        "options": {
            "temperature": 0.05,
            "num_predict": 300,
        },
    }

    try:
        with httpx.Client(timeout=120.0) as client:  # 120s — cold start için yeterli
            resp = client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            if resp.status_code == 404:
                print(f"[LLaVA-Detect] Model '{OLLAMA_VISION_MODEL}' kurulu değil.")
                return []
            resp.raise_for_status()
            raw = resp.json().get("response", "").strip()

            # Markdown kod bloğu temizle
            for marker in ["```json", "```"]:
                if marker in raw:
                    parts = raw.split(marker)
                    raw = parts[1].split("```")[0].strip() if len(parts) > 1 else raw
                    break

            # JSON dizisini bul
            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start != -1 and end > start:
                try:
                    parsed = _json.loads(raw[start:end])
                    if isinstance(parsed, list):
                        cleaned = []
                        for item in parsed:
                            if isinstance(item, dict) and item.get("tur"):
                                cleaned.append({
                                    "tur": str(item.get("tur", "")).lower(),
                                    "renk": str(item.get("renk", "")),
                                    "kumas": str(item.get("kumas", "")),
                                    "stil": str(item.get("stil", "")),
                                })
                        return cleaned
                except _json.JSONDecodeError:
                    pass
            print(f"[LLaVA-Detect] JSON parse edilemedi: {raw[:200]}")
            return []
    except httpx.ConnectError:
        print("[LLaVA-Detect] Ollama bağlantı hatası.")
        return []
    except Exception as e:
        print(f"[LLaVA-Detect] Hata: {e}")
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

    # 1. Görsel varsa llava ile analiz et (FashionSigLIP verisi prompt'a eklenir)
    if image_url:
        image_b64 = _image_to_base64(image_url)
        caption = _caption_with_llava(image_b64, items_desc, style_hint, fashion_analysis)

    # 2. Sadece metin ile dene (llava yoksa veya görsel yoksa)
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
    Optimize edilmiş iki aşamalı pipeline:
    - FashionSigLIP + LLaVA PARALEL çalışır (süre yarıya iner)
    - LLaVA JSON başarısız olursa FashionSigLIP verisiyle hikaye yazılır
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

    # ──── LLaVA ve FashionSigLIP PARALEL çalıştır ──────────────────
    async def run_llava():
        return await loop.run_in_executor(None, _detect_outfit_items_with_llava, image_b64)

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
    llava_task = asyncio.create_task(run_llava())
    siglip_task = asyncio.create_task(run_fashion_siglip())
    detected_items, fashion_analysis = await asyncio.gather(llava_task, siglip_task)
    # ─────────────────────────────────────────────────────────────

    # LLaVA başarısız olduysa FashionSigLIP verisinden item listesi üret
    if not detected_items and fashion_analysis:
        detected_items = [{
            "tur": fashion_analysis.get("tur", "kıyafet"),
            "renk": fashion_analysis.get("renk", ""),
            "kumas": "",
            "stil": fashion_analysis.get("stil_etiketi", ""),
        }]
        print("[Pipeline] LLaVA JSON parse edilemedi, FashionSigLIP verisi kullanılıyor.")

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
    Görseli Ollama llava ile analiz eder ve JSON döner:
    { "tur": "Tişört", "renk": "Kırmızı", "kumas": "Pamuk", "stil": "Gündelik" }
    """
    image_b64 = req.image_b64
    if not image_b64 and req.image_url:
        image_b64 = _image_to_base64(req.image_url)

    if not image_b64:
        raise HTTPException(status_code=400, detail="Lütfen image_url veya image_b64 sağlayın.")

    prompt = (
        "Bu kıyafet fotoğrafını analiz et ve sadece JSON formatında yanıt ver. Başka hiçbir metin ekleme. "
        "Döndüreceğin JSON şu alanları içersin: "
        "'tur' (Örn: Pantolon, Tişört, Gömlek, Etek, Elbise, Kazak), "
        "'renk' (Örn: Mavi, Kırmızı, Siyah), "
        "'kumas' (Örn: Kot, Pamuk, Keten, Yün, Deri), "
        "'stil' (Örn: Gündelik, Spor, Şık, Resmi). "
        "Lütfen çıktının SADECE geçerli bir JSON objesi olduğundan emin ol."
    )

    payload = {
        "model": OLLAMA_VISION_MODEL,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            response_text = data.get("response", "").strip()
            
            # Markdown block parsing (```json ... ```)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            import json
            parsed_data = json.loads(response_text)
            
            return {
                "success": True,
                "data": parsed_data
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"LLaVa analizi başarısız: {str(e)}",
            "data": { "tur": "", "renk": "", "kumas": "", "stil": "" }
        }

