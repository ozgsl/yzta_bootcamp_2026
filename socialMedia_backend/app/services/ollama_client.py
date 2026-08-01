"""
ollama_client.py
----------------
Service layer interacting with local Ollama LLM.
Uses local llama3.2 model running on http://localhost:11434.

Primary functions:
1. get_chat_response() -> Generates chatbot response and extracts context JSON
2. generate_outfit_recommendation() -> Recommends an outfit based on context and clean clothes list
"""

from __future__ import annotations
import json
import os
import re
import httpx
from typing import List, Dict

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def _ollama_chat(messages: List[Dict], temperature: float = 0.7) -> str:
    """Calls Ollama /api/chat endpoint and returns string response."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"]
    except Exception as exc:
        print(f"[Ollama] Connection error: {exc}. Using smart fallback.")
        return ""


def _extract_json(text: str) -> dict:
    """Extracts JSON block from model output."""
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        text = match.group(1)
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"No valid JSON found:\n{text[:300]}")


# ─────────────────────────────────────────────
# 1) CHATBOT
# ─────────────────────────────────────────────

CHATBOT_SYSTEM_PROMPT = """\
Sen dijital gardırop uygulaması için profesyonel bir stilistsin (AI Stylist). KESİNLİKLE sadece Türkçe konuşmalısın. Anlamsız çeviriler (örn. göğüs ayarı vb.) veya yabancı kelimeler KULLANMA. Doğal ve sıcak bir dille kullanıcıyla sohbet et ve şunları öğren:
- Nereye gidiyor / ne yapıyor (etkinlik: iş, randevu, spor, gezi vb.)
- Hava durumu (bilmiyorsan kibarca sor)
- Stil tercihi (rahat, şık, spor vb.)

Eğer kullanıcı sana kombin önerisi sorarsa veya yeterince bilgi topladığını düşünüyorsan, ona kullanıcının gardırobundaki mevcut kıyafetlerden bir kombin ÖNER.
Bunun için kullanıcının kıyafet listesini referans al ve seçtiğin kıyafetlerin ID'lerini 'onerilen_kiyafet_idleri' listesinde döndür. 
Sadece sana verilen listedeki kıyafet ID'lerini kullan.

Kurallar:
- Sadece Türkçe, sıcak ve kısa cümleler kur. Aynı anda sadece bir soru sor.
- Yeterli bilgi alana kadar sohbeti sürdür. (Örn. en azından hava durumu ve etkinlik bilgisi)
- Bir kombin önerdiğinde kıyafetleri neden seçtiğini açıkla.
- Asla sana verilen gardırop listesi dışından bir kıyafet varmış gibi davranma.

HER ZAMAN yanıtını aşağıdaki JSON formatında ver:
{
  "asistan_mesaji": "...",
  "baglam": {"etkinlik": "...", "hava_durumu": "...", "stil_tercihi": "..."},
  "hazir_mi": false,
  "onerilen_kiyafet_idleri": [1, 2] // Eğer kombin öneriyorsan seçtiğin ID'leri listele, önermiyorsan boş liste bırak []
}"""


def get_chat_response(history: List[Dict], new_message: str, available_clothes: List[Dict] = None) -> dict:
    """
    history: [{"rol": "user"/"assistant", "mesaj": "..."}]
    new_message: User's new chat message
    available_clothes: [{"id": 1, "isim": "...", ...}]

    Returns:
    {"asistan_mesaji": "...", "baglam": {...}, "hazir_mi": bool, "onerilen_kiyafet_idleri": [...]}
    """
    system_content = CHATBOT_SYSTEM_PROMPT
    if available_clothes:
        clothes_info = []
        for c in available_clothes:
            clothes_info.append(f"[ID: {c.get('id')}] {c.get('kategori', '')} - {c.get('renk', '')} - {c.get('isim', '')}")
        system_content += "\n\nKULLANICININ GARDIROBUNDAKİ KIYAFETLER:\n" + "\n".join(clothes_info)

    messages = [{"role": "system", "content": system_content}]
    for m in history:
        role = "user" if m.get("rol") == "user" or m.get("role") == "user" else "assistant"
        content = m.get("mesaj") or m.get("content") or ""
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": new_message})

    raw = _ollama_chat(messages, temperature=0.7)
    if not raw:
        # Smart fallback when Ollama server is offline
        return {
            "asistan_mesaji": "Harika! Gardırobundaki en uygun kıyafetleri inceleyip sana özel kombinini hazırlıyorum ✨",
            "baglam": {
                "etkinlik": "Günlük",
                "hava_durumu": "Güzel",
                "stil_tercihi": "Rahat",
            },
            "hazir_mi": True,
        }

    try:
        return _extract_json(raw)
    except ValueError:
        return {
            "asistan_mesaji": raw,
            "baglam": {},
            "hazir_mi": False,
        }


# ─────────────────────────────────────────────
# 2) OUTFIT RECOMMENDATION GENERATOR
# ─────────────────────────────────────────────

RECOMMENDER_SYSTEM_PROMPT = """\
You are an expert AI fashion stylist. Select 2-4 items from the available wardrobe list for the given context.
Rules:
- Select from clean items provided in the list.
- Return output strictly in JSON format.
"""


def generate_outfit_recommendation(context: dict, clean_clothes: List[Dict]) -> dict:
    """
    context: {"etkinlik": "...", "hava_durumu": "...", "stil_tercihi": "..."}
    clean_clothes: List of clean clothes dicts

    Returns:
    {"secilen_kiyafet_idleri": [int, ...], "aciklama": "..."}
    """
    if not clean_clothes:
        return {"secilen_kiyafet_idleri": [], "aciklama": "Dolabında temiz kıyafet bulunamadı."}

    # Rule-based matching fallback
    selected_ids = []
    top = next((c for c in clean_clothes if c.get("tur", "").lower() in ["tişört", "t-shirt", "gömlek", "bluz", "kazak", "sweatshirt", "üst giyim"]), None)
    bottom = next((c for c in clean_clothes if c.get("tur", "").lower() in ["pantolon", "şort", "etek", "alt giyim", "jean"]), None)
    shoes = next((c for c in clean_clothes if c.get("tur", "").lower() in ["ayakkabı", "sneaker", "bot"]), None)
    accessory = next((c for c in clean_clothes if c.get("tur", "").lower() in ["çanta", "aksesuar", "ceket", "mont"]), None)

    if top:
        selected_ids.append(top["id"])
    if bottom:
        selected_ids.append(bottom["id"])
    if shoes:
        selected_ids.append(shoes["id"])
    if accessory and len(selected_ids) < 4:
        selected_ids.append(accessory["id"])

    if not selected_ids:
        selected_ids = [c["id"] for c in clean_clothes[:3]]

    event = context.get("etkinlik", "günlük kullanım")
    weather = context.get("hava_durumu", "normal hava")

    # Kıyafet listesini AI için zengin formatta hazırla (foto_url dahil)
    clothes_summary = []
    for c in clean_clothes:
        entry = (
            f"ID:{c['id']} | Tür:{c.get('tur','?')} | Renk:{c.get('renk','?')} "
            f"| Stil:{c.get('stil_etiketi','?')} | Mevsim:{c.get('mevsim','?')}"
        )
        if c.get("marka"):
            entry += f" | Marka:{c['marka']}"
        if c.get("beden"):
            entry += f" | Beden:{c['beden']}"
        if c.get("foto_url"):
            entry += f" | Foto:{c['foto_url']}"
        clothes_summary.append(entry)

    clothes_text = "\n".join(clothes_summary)

    prompt_messages = [
        {"role": "system", "content": RECOMMENDER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Etkinlik: {context.get('etkinlik', '?')}\n"
                f"Hava durumu: {context.get('hava_durumu', '?')}\n"
                f"Stil tercihi: {context.get('stil_tercihi', 'belirtilmedi')}\n\n"
                f"Kullanıcının temiz kıyafetleri (her satır bir parça):\n{clothes_text}\n\n"
                "Yukarıdaki kıyafetlerden 2-4 tanesini seçerek kombin öner. "
                "Renk uyumu, mevsim ve etkinliğe uygunluğa dikkat et. "
                "Yanıtı SADECE JSON olarak ver:\n"
                "{\"secilen_kiyafet_idleri\": [id1, id2, ...], \"aciklama\": \"...\"}"
            ),
        },
    ]

    raw = _ollama_chat(prompt_messages, temperature=0.3)
    if raw:
        try:
            res = _extract_json(raw)
            if res.get("secilen_kiyafet_idleri"):
                return res
        except Exception:
            pass

    return {
        "secilen_kiyafet_idleri": selected_ids,
        "aciklama": f"{event.capitalize()} ve {weather} şartları için gardırobundan özenle seçilen şık kombin önerisi ✨",
    }


# Backwards compatibility aliases
sohbet_yaniti_al = get_chat_response
kombin_onerisi_uret = generate_outfit_recommendation