"""
FashionSigLIP Kıyafet Sınıflandırma Servisi
=============================================
Model: Marqo/marqo-fashionSigLIP
Kaynak: https://huggingface.co/Marqo/marqo-fashionSigLIP

Bu servis, kullanıcı tarafından yüklenen kıyafet görsellerini
sıfır-atış (zero-shot) CLIP tabanlı sınıflandırma ile analiz eder.
Uygulama başlatıldığında model bir kez yüklenir ve bellekte tutulur.

NOT: FashionSigLIP İngilizce metin ile eğitilmiş bir modeldir.
     Modele İngilizce promptlar gönderilir, çıktılar Türkçe'ye çevrilir.
"""
from __future__ import annotations

import base64
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Etiket Setleri — İngilizce (model için) + Türkçe haritaları (çıktı için)
# ---------------------------------------------------------------------------

KIYAFET_TURLERI_EN = [
    "t-shirt", "shirt", "blouse", "sweater", "cardigan", "sweatshirt", "hoodie",
    "jacket", "blazer", "coat", "parka", "vest",
    "trousers", "jeans", "shorts", "leggings", "sweatpants",
    "skirt", "dress", "jumpsuit",
    "sneakers", "boots", "heels", "loafers", "sandals",
    "bag", "backpack", "handbag",
    "hat", "beanie", "scarf", "belt", "tie", "accessory",
]

TUR_TR_MAP = {
    "t-shirt": "tişört", "shirt": "gömlek", "blouse": "bluz",
    "sweater": "kazak", "cardigan": "hırka", "sweatshirt": "sweatshirt",
    "hoodie": "hoodie", "jacket": "ceket", "blazer": "blazer",
    "coat": "mont", "parka": "kaban", "vest": "yelek",
    "trousers": "pantolon", "jeans": "jean", "shorts": "şort",
    "leggings": "tayt", "sweatpants": "eşofman altı",
    "skirt": "etek", "dress": "elbise", "jumpsuit": "tulum",
    "sneakers": "spor ayakkabı", "boots": "bot", "heels": "topuklu ayakkabı",
    "loafers": "loafer", "sandals": "sandalet",
    "bag": "çanta", "backpack": "sırt çantası", "handbag": "el çantası",
    "hat": "şapka", "beanie": "bere", "scarf": "eşarp",
    "belt": "kemer", "tie": "kravat", "accessory": "aksesuar",
}

RENKLER_EN = [
    "black", "white", "gray", "navy blue", "blue", "light blue",
    "red", "pink", "purple", "lilac",
    "green", "khaki", "olive green",
    "yellow", "orange", "beige", "cream", "brown", "nude",
    "multicolor", "patterned",
]

RENK_TR_MAP = {
    "black": "siyah", "white": "beyaz", "gray": "gri", "navy blue": "lacivert",
    "blue": "mavi", "light blue": "açık mavi", "red": "kırmızı", "pink": "pembe",
    "purple": "mor", "lilac": "lila", "green": "yeşil", "khaki": "haki",
    "olive green": "zeytin yeşili", "yellow": "sarı", "orange": "turuncu",
    "beige": "bej", "cream": "krem", "brown": "kahverengi", "nude": "ten rengi",
    "multicolor": "çok renkli", "patterned": "desenli",
}

STILLER_EN = [
    "casual", "sporty", "elegant", "formal", "business",
    "streetwear", "bohemian", "classic", "minimalist", "vintage",
]

STIL_TR_MAP = {
    "casual": "gündelik", "sporty": "spor", "elegant": "şık",
    "formal": "resmi", "business": "iş", "streetwear": "sokak modu",
    "bohemian": "bohem", "classic": "klasik",
    "minimalist": "minimalist", "vintage": "vintage",
}

MEVSIMLER_EN = [
    "spring", "summer", "autumn", "winter", "all season",
]

MEVSIM_TR_MAP = {
    "spring": "ilkbahar", "summer": "yaz", "autumn": "sonbahar",
    "winter": "kış", "all season": "tüm sezon",
}

# post_outfit_items.category CHECK constraint değerleri
UST_KATEGORILER = {
    "üst giyim": ["t-shirt", "shirt", "blouse", "sweater", "cardigan", "sweatshirt", "hoodie", "blazer", "vest"],
    "alt giyim": ["trousers", "jeans", "shorts", "leggings", "sweatpants", "skirt"],
    "elbise/tulum": ["dress", "jumpsuit"],
    "dış giyim": ["jacket", "coat", "parka"],
    "ayakkabı": ["sneakers", "boots", "heels", "loafers", "sandals"],
    "aksesuar": ["bag", "backpack", "handbag", "hat", "beanie", "scarf", "belt", "tie", "accessory"],
}

POST_CATEGORY_MAP = {
    "üst giyim": "üst giyim",
    "alt giyim": "alt giyim",
    "elbise/tulum": "üst giyim",
    "dış giyim": "dış giyim",
    "ayakkabı": "ayakkabı",
    "aksesuar": "aksesuar",
}


# ---------------------------------------------------------------------------
# Yardımcı — İngilizce kıyafet türü → post_outfit_items.category
# ---------------------------------------------------------------------------

def _tur_to_post_category(tur_en: str) -> str:
    """İngilizce kıyafet türünü veritabanı category değerine çevirir."""
    tur_lower = tur_en.lower()
    for ust_kat, alt_liste in UST_KATEGORILER.items():
        if any(alt.lower() == tur_lower for alt in alt_liste):
            return POST_CATEGORY_MAP.get(ust_kat, "diğer")
    return "diğer"


# ---------------------------------------------------------------------------
# FashionClassifier — Singleton
# ---------------------------------------------------------------------------

class FashionClassifier:
    """
    FashionSigLIP modelini saran singleton sınıf.
    Uygulama başlatıldığında load() çağrılır, model bellekte tutulur.
    """

    _instance: FashionClassifier | None = None
    _initialized: bool = False

    def __new__(cls) -> FashionClassifier:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.model = None
        self.processor = None
        self.tokenizer = None
        self._load_error: str | None = None
        self._initialized = True

    # -----------------------------------------------------------------------

    def load(self) -> bool:
        """
        Modeli HuggingFace'den indirir / cache'den yükler.
        Başarılıysa True, hata olursa False döner.
        """
        if self.model is not None:
            return True  # Zaten yüklü

        try:
            import open_clip  # type: ignore
            logger.info("[FashionSigLIP] Model yükleniyor: Marqo/marqo-fashionSigLIP ...")

            model, _, preprocess = open_clip.create_model_and_transforms(
                "hf-hub:Marqo/marqo-fashionSigLIP"
            )
            tokenizer = open_clip.get_tokenizer("hf-hub:Marqo/marqo-fashionSigLIP")
            model.eval()

            self.model = model
            self.processor = preprocess
            self.tokenizer = tokenizer

            logger.info("[FashionSigLIP] ✅ Model başarıyla yüklendi.")
            return True

        except Exception as exc:
            self._load_error = str(exc)
            logger.error(f"[FashionSigLIP] ❌ Model yüklenemedi: {exc}")
            return False

    @property
    def is_ready(self) -> bool:
        return self.model is not None

    # -----------------------------------------------------------------------
    # Görsel Yükleme
    # -----------------------------------------------------------------------

    def _load_pil_image(
        self,
        image_path: Path | None = None,
        image_b64: str | None = None,
        image_bytes: bytes | None = None,
    ):
        """PIL.Image döner. Kaynak: dosya yolu, base64 veya ham bytes."""
        from PIL import Image  # type: ignore

        if image_bytes:
            return Image.open(io.BytesIO(image_bytes)).convert("RGB")
        if image_b64:
            raw = base64.b64decode(image_b64)
            return Image.open(io.BytesIO(raw)).convert("RGB")
        if image_path and Path(image_path).exists():
            return Image.open(image_path).convert("RGB")
        raise ValueError("Görsel kaynağı sağlanmadı (path/b64/bytes).")

    # -----------------------------------------------------------------------
    # Zero-Shot Sınıflandırma
    # -----------------------------------------------------------------------

    def _top_label(self, image, candidates: list, top_k: int = 3) -> list:
        """
        Görsel ile aday metin listesini karşılaştırır.
        En yüksek cosine benzerlik skorlu top_k sonucu döner.
        """
        import torch  # type: ignore

        img_tensor = self.processor(image).unsqueeze(0)
        texts = self.tokenizer(candidates)

        with torch.no_grad():
            img_feat = self.model.encode_image(img_tensor)
            txt_feat = self.model.encode_text(texts)

            img_feat = img_feat / img_feat.norm(dim=-1, keepdim=True)
            txt_feat = txt_feat / txt_feat.norm(dim=-1, keepdim=True)

            similarity = (img_feat @ txt_feat.T).squeeze(0)
            probs = similarity.softmax(dim=-1).tolist()

        scored = sorted(zip(candidates, probs), key=lambda x: x[1], reverse=True)
        return [{"label": lbl, "score": round(sc, 4)} for lbl, sc in scored[:top_k]]

    # -----------------------------------------------------------------------
    # Ana Sınıflandırma Metodu
    # -----------------------------------------------------------------------

    def classify_image(
        self,
        image_path: Path | None = None,
        image_b64: str | None = None,
        image_bytes: bytes | None = None,
    ) -> dict:
        """
        Kıyafet görselini analiz eder.
        Model İngilizce prompt'larla çalışır, sonuçlar Türkçe'ye çevrilir.

        Dönen dict:
            tur           → kiyafetler.tur         (Türkçe)
            renk          → kiyafetler.renk         (Türkçe)
            stil_etiketi  → kiyafetler.stil_etiketi (Türkçe)
            mevsim        → kiyafetler.mevsim       (Türkçe)
            post_category → post_outfit_items.category
            confidence    → float (0-1)
            alternatifler → top-3 tur listesi       (Türkçe)
        """
        if not self.is_ready:
            return {"success": False, "error": f"Model yüklü değil: {self._load_error}"}

        try:
            image = self._load_pil_image(image_path, image_b64, image_bytes)

            # 1) Kıyafet türü — İngilizce etiketlerle
            tur_results_en = self._top_label(image, KIYAFET_TURLERI_EN, top_k=3)
            best_tur_en = tur_results_en[0]["label"]

            # 2) Renk
            best_renk_en = self._top_label(image, RENKLER_EN, top_k=1)[0]["label"]

            # 3) Stil
            best_stil_en = self._top_label(image, STILLER_EN, top_k=1)[0]["label"]

            # 4) Mevsim
            best_mevsim_en = self._top_label(image, MEVSIMLER_EN, top_k=1)[0]["label"]

            # 5) İngilizce → Türkçe çeviri
            alternatifler_tr = [
                {"label": TUR_TR_MAP.get(r["label"], r["label"]), "score": r["score"]}
                for r in tur_results_en
            ]

            return {
                "success": True,
                "tur": TUR_TR_MAP.get(best_tur_en, best_tur_en),
                "renk": RENK_TR_MAP.get(best_renk_en, best_renk_en),
                "stil_etiketi": STIL_TR_MAP.get(best_stil_en, best_stil_en),
                "mevsim": MEVSIM_TR_MAP.get(best_mevsim_en, best_mevsim_en),
                "post_category": _tur_to_post_category(best_tur_en),
                "confidence": tur_results_en[0]["score"],
                "alternatifler": alternatifler_tr,
            }

        except Exception as exc:
            logger.error(f"[FashionSigLIP] Sınıflandırma hatası: {exc}")
            return {"success": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Singleton & startup helper
# ---------------------------------------------------------------------------

classifier = FashionClassifier()


def load_model_on_startup() -> None:
    """main.py lifespan'ından çağrılır. Model başlatma sırasında yüklenir."""
    classifier.load()
