#!/usr/bin/env python3
"""
Moondream2 Test — Describe → Parse yaklaşımı
Kullanim: python scripts/test_moondream.py /yol/kiyafet.jpg
"""
import sys, base64, re, httpx
from pathlib import Path

OLLAMA = "http://localhost:11434"
MODEL  = "moondream"

_TIP_MAP = {
    "polo shirt":"gomlek","polo":"gomlek","shirt":"gomlek","t-shirt":"tisort",
    "tshirt":"tisort","top":"tisort","blouse":"bluz","sweater":"kazak","hoodie":"hirka",
    "sweatshirt":"hirka","cardigan":"hirka","vest":"yelek","dress":"elbise",
    "gown":"elbise","suit":"takim","blazer":"ceket","jacket":"ceket","coat":"mont",
    "pants":"pantolon","trousers":"pantolon","jeans":"pantolon","skirt":"etek",
    "leggings":"tayt","shorts":"sort","shoes":"ayakkabi","sneakers":"spor ayakkabi",
    "boots":"bot","sandals":"sandalet","heels":"topuklu","loafers":"ayakkabi",
    "bag":"canta","backpack":"canta","hat":"sapka","scarf":"atki","belt":"kemer",
}
_KAT_MAP = {
    "gomlek":"ust giyim","tisort":"ust giyim","bluz":"ust giyim","kazak":"ust giyim",
    "hirka":"ust giyim","yelek":"ust giyim","elbise":"ust giyim","takim":"ust giyim",
    "ceket":"dis giyim","mont":"dis giyim",
    "pantolon":"alt giyim","etek":"alt giyim","tayt":"alt giyim","sort":"alt giyim",
    "ayakkabi":"ayakkabi","spor ayakkabi":"ayakkabi","bot":"ayakkabi",
    "sandalet":"ayakkabi","topuklu":"ayakkabi",
    "canta":"aksesuar","sapka":"aksesuar","atki":"aksesuar","kemer":"aksesuar",
}
_COLORS = {
    "white":"beyaz","black":"siyah","gray":"gri","grey":"gri",
    "navy":"lacivert","blue":"mavi","light blue":"mavi","dark blue":"lacivert",
    "red":"kirmizi","green":"yesil","yellow":"sari","orange":"turuncu",
    "pink":"pembe","purple":"mor","brown":"kahverengi","beige":"bej","cream":"krem",
    "khaki":"bej","olive":"yesil","maroon":"bordo",
}
_TARZ_EN = {"casual":"casual","formal":"resmi","sporty":"spor","elegant":"sik",
             "sport":"spor","chic":"sik","vintage":"vintage","business":"resmi"}
_DESEN_EN = {"solid":"duz","stripe":"cizgili","stripes":"cizgili","check":"kareli",
              "checkered":"kareli","pattern":"desenli","print":"baskili","printed":"baskili"}


def parse_description(text: str) -> list:
    t = text.lower()
    # Tarz
    tarz = "casual"
    for en, tr in _TARZ_EN.items():
        if en in t: tarz = tr; break
    # Desen
    desen = "duz"
    for en, tr in _DESEN_EN.items():
        if en in t: desen = tr; break

    items = []
    garments = list(_TIP_MAP.items())  # sıra önemli: polo shirt > polo
    for en_g, tr_g in garments:
        if en_g not in t:
            continue
        idx = t.find(en_g)
        prefix = t[max(0,idx-35):idx]
        renk = "belirsiz"
        for c_en, c_tr in _COLORS.items():
            if c_en in prefix: renk = c_tr; break
        kat = _KAT_MAP.get(tr_g, "ust giyim")
        items.append({"kategori":kat,"tip":tr_g,"renk":renk,
                      "desen":desen,"tarz":tarz,"malzeme_tahmini":None,
                      "confidence":0.85,"tur":tr_g,"stil":tarz})

    # Dedup (tip bazında)
    seen, uniq = set(), []
    for it in items:
        if it["tip"] not in seen:
            seen.add(it["tip"]); uniq.append(it)

    if not uniq:
        genel_renk = next((tr for en,tr in _COLORS.items() if en in t), "belirsiz")
        uniq = [{"kategori":"ust giyim","tip":"kiyafet","renk":genel_renk,
                 "desen":desen,"tarz":tarz,"malzeme_tahmini":None,
                 "confidence":0.5,"tur":"kiyafet","stil":tarz}]
    return uniq


def main():
    import json
    print("=" * 55)
    print("  Moondream2 — Describe → Parse Test")
    print("=" * 55)

    try:
        resp = httpx.get(f"{OLLAMA}/api/tags", timeout=5.0)
        models = [m["name"] for m in resp.json().get("models",[])]
        print(f"[OK] Ollama: {models}")
        if not any(MODEL in m for m in models):
            print(f"[!] '{MODEL}' kurulu degil: ollama pull {MODEL}")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Ollama: {e}"); sys.exit(1)

    if len(sys.argv) < 2:
        print("[!] Kullanim: python scripts/test_moondream.py /yol/kiyafet.jpg")
        sys.exit(0)

    img_path = sys.argv[1]
    if not Path(img_path).exists():
        print(f"[!] Dosya yok: {img_path}"); sys.exit(1)

    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    print(f"[OK] Gorsel: {img_path}\n")

    print("Moondream'e aciklama soruluyor...")
    r = httpx.post(f"{OLLAMA}/api/generate", json={
        "model": MODEL,
        "prompt": (
            "Describe the clothing worn by the person in this photo. "
            "Include every item: shirt, pants, shoes, jacket, accessories. "
            "Mention the color of each item and the overall style (casual/formal/sporty)."
        ),
        "images": [b64],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 150},
    }, timeout=120.0)
    description = r.json().get("response","").strip()
    print(f"\nMoondream aciklamasi:\n  {description}\n")

    items = parse_description(description)
    print(f"Parse sonucu ({len(items)} item):")
    print(json.dumps(items, ensure_ascii=False, indent=2))

    print(f"\nFashionSigLIP embedding:")
    for it in items:
        q = f"{it['tip']} {it['renk']} {it['desen']} {it['tarz']}"
        print(f"  -> \"{q}\"")

if __name__ == "__main__":
    main()
