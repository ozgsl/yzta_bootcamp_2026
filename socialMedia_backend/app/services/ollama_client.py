"""
ollama_client.py (eski adı: gemini_client.py)
---------------------------------------------
Yerel Ollama LLM ile konuşan servis katmanı.
Gemini API yerine http://localhost:11434 üzerinde çalışan
yerel llama3.2 modeli kullanılır.

İki ana fonksiyon:
1. sohbet_yaniti_al()    -> Chatbot mesajına yanıt üretir + bağlam JSON çıkarır
2. kombin_onerisi_uret() -> Bağlam + temiz kıyafet listesine göre kombin önerir
"""

from __future__ import annotations
import json
import os
import re
import httpx
from typing import List, Dict

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3.2")


def _ollama_chat(messages: List[Dict], temperature: float = 0.7) -> str:
    """Ollama /api/chat endpoint'ini çağırır, string yanıt döner."""
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
    """Model çıktısından JSON bloğunu ayıklar."""
    # ```json ... ``` bloğu varsa içini al
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        text = match.group(1)
    # Ham JSON bul
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    raise ValueError(f"Geçerli JSON bulunamadı:\n{text[:300]}")


# ─────────────────────────────────────────────
# 1) CHATBOT
# ─────────────────────────────────────────────

CHATBOT_SISTEM_PROMPTU = """\
Sen "Akıllı Dolap" uygulamasının moda asistanısın. Görevin kullanıcıyla
kısa ve doğal sohbet ederek şunları öğrenmek:
- Nereye gidiyor / ne yapacak (etkinlik: iş, randevu, spor, gezi, parti vb.)
- Hava durumu (bilmiyorsa nazikçe sor)
- Varsa stil tercihi (rahat, şık, spor vb.)

Kurallar:
- Sıcak, samimi ve kısa cümlelerle yaz. Tek seferde tek soru sor.
- Yeterli bilgi (en az etkinlik + hava) toplayana kadar sohbete devam et.
- Hazır olunca "harika, hazırlanıyorum" gibi bir kapanış yap, hazir_mi = true yap.

YANITI MUTLAKA aşağıdaki JSON formatında ver, başka hiçbir şey yazma:
{
  "asistan_mesaji": "...",
  "baglam": {"etkinlik": "...", "hava_durumu": "...", "stil_tercihi": "..."},
  "hazir_mi": false
}"""


def sohbet_yaniti_al(gecmis: List[Dict], yeni_mesaj: str) -> dict:
    """
    gecmis: [{"rol": "user"/"assistant", "mesaj": "..."}]
    yeni_mesaj: kullanıcının yeni mesajı

    Dönen:
    {"asistan_mesaji": "...", "baglam": {...}, "hazir_mi": bool}
    """
    messages = [{"role": "system", "content": CHATBOT_SISTEM_PROMPTU}]
    for m in gecmis:
        role = "user" if m["rol"] == "user" else "assistant"
        messages.append({"role": role, "content": m["mesaj"]})
    messages.append({"role": "user", "content": yeni_mesaj})

    raw = _ollama_chat(messages, temperature=0.7)
    if not raw:
        # Ollama kapalıysa akıllı fallback
        return {
            "asistan_mesaji": f"Harika! {yeni_mesaj} için şık bir kombin hazırlıyorum ✨",
            "baglam": {"etkinlik": yeni_mesaj, "hava_durumu": "güneşli", "stil_tercihi": "gündelik"},
            "hazir_mi": True,
        }

    try:
        result = _extract_json(raw)
    except ValueError:
        # JSON parse edilemezse güvenli fallback
        result = {
            "asistan_mesaji": raw.strip()[:500] or "Anladım, kombininizi hazırlıyorum!",
            "baglam": {"etkinlik": yeni_mesaj, "hava_durumu": "", "stil_tercihi": ""},
            "hazir_mi": True,
        }

    # Zorunlu anahtarların varlığını garanti et
    result.setdefault("asistan_mesaji", "")
    result.setdefault("baglam", {})
    result.setdefault("hazir_mi", False)
    result["baglam"].setdefault("etkinlik", "")
    result["baglam"].setdefault("hava_durumu", "")
    result["baglam"].setdefault("stil_tercihi", "")
    return result


# ─────────────────────────────────────────────
# 2) KOMBİN ÖNERİSİ
# ─────────────────────────────────────────────

KOMBIN_SISTEM_PROMPTU = """\
Sen bir moda stilistisin. Sana bir bağlam (etkinlik, hava durumu, stil tercihi)
ve kullanıcının dolabındaki TEMİZ kıyafetlerin listesi verilecek.

Görevin: Bu kıyafetler arasından verilen bağlama en uygun KOMBİNİ seçmek.
Sadece verilen kıyafet ID'lerini kullan; var olmayan kıyafet icat etme.

YANITI MUTLAKA aşağıdaki JSON formatında ver, başka hiçbir şey yazma:
{
  "secilen_kiyafet_idleri": [1, 2, 3],
  "aciklama": "Kombinin neden uygun olduğuna dair kısa açıklama"
}"""


def kombin_onerisi_uret(baglam: dict, temiz_kiyafetler: List[Dict]) -> dict:
    """
    baglam: {"etkinlik": "...", "hava_durumu": "...", "stil_tercihi": "..."}
    temiz_kiyafetler: kiyafetleri_getir(sadece_temiz=True) çıktısı

    Dönen:
    {"secilen_kiyafet_idleri": [...], "aciklama": "..."}
    """
    if not temiz_kiyafetler:
        return {"secilen_kiyafet_idleri": [], "aciklama": "Dolabında hiç temiz kıyafet bulunamadı."}

    kiyafet_listesi = json.dumps(temiz_kiyafetler, ensure_ascii=False, indent=2)
    kullanici_mesaji = f"""
BAĞLAM:
{json.dumps(baglam, ensure_ascii=False, indent=2)}

KULLANICININ TEMİZ KIYAFETLERİ:
{kiyafet_listesi}

Lütfen bu bağlama en uygun kombini yalnızca yukarıdaki kıyafet ID'lerini kullanarak öner.
"""
    messages = [
        {"role": "system", "content": KOMBIN_SISTEM_PROMPTU},
        {"role": "user",   "content": kullanici_mesaji},
    ]
    raw = _ollama_chat(messages, temperature=0.8)
    
    if not raw:
        # Akıllı kural tabanlı kombin eşleştirme (Ollama kapalı durumlar için)
        ustler = [k for k in temiz_kiyafetler if any(t in str(k.get("tur", "")).lower() for t in ["tişört", "gömlek", "bluz", "kazak", "hırka", "sweatshirt", "hoodie", "ceket", "üst"])]
        altlar = [k for k in temiz_kiyafetler if any(t in str(k.get("tur", "")).lower() for t in ["pantolon", "jean", "kot", "şort", "tayt", "eşofman", "etek", "alt"])]
        digerleri = [k for k in temiz_kiyafetler if k not in ustler and k not in altlar]

        secilen = []
        if ustler: secilen.append(ustler[0]["id"])
        if altlar: secilen.append(altlar[0]["id"])
        if digerleri: secilen.append(digerleri[0]["id"])
        if not secilen: secilen = [k["id"] for k in temiz_kiyafetler[:3]]

        etkinlik = baglam.get("etkinlik", "günlük kullanım")
        return {
            "secilen_kiyafet_idleri": secilen,
            "aciklama": f"'{etkinlik}' etkinliği için dolabındaki en uyumlu parçalardan özel bir kombin oluşturuldu ✨"
        }

    try:
        result = _extract_json(raw)
    except ValueError:
        result = {
            "secilen_kiyafet_idleri": [k["id"] for k in temiz_kiyafetler[:3]],
            "aciklama": raw.strip()[:300] or "Kombin önerisi oluşturuldu.",
        }

    result.setdefault("secilen_kiyafet_idleri", [])
    result.setdefault("aciklama", "")
    return result