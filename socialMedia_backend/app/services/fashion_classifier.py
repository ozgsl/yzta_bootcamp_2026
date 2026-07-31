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

import io
import base64
import logging
from pathlib import Path
from typing import Optional

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

# ── YENİ: Kullanıcının verdiği script ile birebir aynı 6 özellik seti ──────
ATTRIBUTE_LABELS = {
    "category": [
        "t-shirt", "shirt", "blouse", "sweater", "hoodie",
        "jacket", "coat", "jeans", "trousers", "shorts",
        "skirt", "dress", "suit", "sneakers", "boots",
        "sandals", "hat", "scarf", "bag",
    ],
    "color": [
        "black", "white", "gray", "beige", "brown", "red", "orange",
        "yellow", "green", "blue", "navy", "purple", "pink", "multicolor",
    ],
    "pattern": [
        "solid / plain", "striped", "plaid / checkered", "floral",
        "polka dot", "animal print", "graphic print", "geometric pattern",
    ],
    "material": [
        "cotton", "denim", "wool", "leather", "linen", "silk",
        "polyester / synthetic", "knit", "corduroy", "velvet",
    ],
    "season": [
        "spring", "summer", "autumn", "winter", "all-season",
    ],
    "occasion": [
        "casual everyday wear", "formal / office wear", "sportswear / athletic",
        "party / evening wear", "loungewear", "outdoor / travel wear",
    ],
}

# İngilizce → Türkçe çeviri haritaları (yeni özellikler)
PATTERN_TR_MAP = {
    "solid / plain": "düz", "striped": "çizgili", "plaid / checkered": "ekose",
    "floral": "çiçekli", "polka dot": "puantiyeli", "animal print": "hayvan deseni",
    "graphic print": "baskılı", "geometric pattern": "geometrik desen",
}

MATERIAL_TR_MAP = {
    "cotton": "pamuk", "denim": "denim", "wool": "yün", "leather": "deri",
    "linen": "keten", "silk": "ipek", "polyester / synthetic": "sentetik",
    "knit": "triko", "corduroy": "fitilli kadife", "velvet": "kadife",
}

OCCASION_TR_MAP = {
    "casual everyday wear": "günlük kullanım",
    "formal / office wear": "resmi / iş",
    "sportswear / athletic": "spor",
    "party / evening wear": "parti / gece",
    "loungewear": "ev kıyafeti",
    "outdoor / travel wear": "dış mekan / seyahat",
}

# Geniş renk haritası (ATTRIBUTE_LABELS["color"] için)
ATTR_COLOR_TR_MAP = {
    "black": "siyah", "white": "beyaz", "gray": "gri", "beige": "bej",
    "brown": "kahverengi", "red": "kırmızı", "orange": "turuncu",
    "yellow": "sarı", "green": "yeşil", "blue": "mavi", "navy": "lacivert",
    "purple": "mor", "pink": "pembe", "multicolor": "çok renkli",
}

# Geniş kategori haritası (ATTRIBUTE_LABELS["category"] için)
ATTR_CATEGORY_TR_MAP = {
    "t-shirt": "tişört", "shirt": "gömlek", "blouse": "bluz",
    "sweater": "kazak", "hoodie": "hoodie", "jacket": "ceket",
    "coat": "mont", "jeans": "jean", "trousers": "pantolon",
    "shorts": "şort", "skirt": "etek", "dress": "elbise",
    "suit": "takım elbise", "sneakers": "spor ayakkabı", "boots": "bot",
    "sandals": "sandalet", "hat": "şapka", "scarf": "eşarp", "bag": "çanta",
}

ATTR_SEASON_TR_MAP = {
    "spring": "ilkbahar", "summer": "yaz", "autumn": "sonbahar",
    "winter": "kış", "all-season": "tüm sezon",
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

    _instance: Optional["FashionClassifier"] = None
    _initialized: bool = False

    def __new__(cls) -> "FashionClassifier":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self.model = None
        self.processor = None
        self.tokenizer = None
        self._load_error: Optional[str] = None
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
        image_path: Optional[Path] = None,
        image_b64: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
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
        image_path: Optional[Path] = None,
        image_b64: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
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

    # -----------------------------------------------------------------------
    # YENİ: Tüm özellik gruplarını sınıflandır (kullanıcının script'i ile aynı)
    # -----------------------------------------------------------------------

    def classify_all_attributes(
        self,
        image_path: Optional[Path] = None,
        image_b64: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> dict:
        """
        Kıyafetin 6 özelliğini FashionSigLIP ile sıfır-atış sınıflandırmasıyla belirler:
        category, color, pattern, material, season, occasion.

        Her özellik için:
            best      → en yüksek skorlu etiket (Türkçe)
            best_en   → İngilizce orijinal (Moondream prompt için)
            confidence → float 0-1
            top_3     → liste

        Hata durumunda {"success": False, "error": ...} döner.
        """
        if not self.is_ready:
            return {"success": False, "error": f"Model yüklü değil: {self._load_error}"}

        try:
            image = self._load_pil_image(image_path, image_b64, image_bytes)
            result: dict = {"success": True}

            TR_MAPS = {
                "category": ATTR_CATEGORY_TR_MAP,
                "color":    ATTR_COLOR_TR_MAP,
                "pattern":  PATTERN_TR_MAP,
                "material": MATERIAL_TR_MAP,
                "season":   ATTR_SEASON_TR_MAP,
                "occasion": OCCASION_TR_MAP,
            }

            for attr_name, labels in ATTRIBUTE_LABELS.items():
                top = self._top_label(image, labels, top_k=3)
                best_en = top[0]["label"]
                tr_map  = TR_MAPS.get(attr_name, {})
                best_tr = tr_map.get(best_en, best_en)

                result[attr_name] = {
                    "best":       best_tr,
                    "best_en":    best_en,
                    "confidence": round(top[0]["score"], 3),
                    "top_3": [
                        {"label": tr_map.get(r["label"], r["label"]),
                         "label_en": r["label"],
                         "score": round(r["score"], 3)}
                        for r in top
                    ],
                }

            # post_category ek bilgi
            cat_en = result["category"]["best_en"]
            result["post_category"] = _tur_to_post_category(cat_en)

            return result

        except Exception as exc:
            logger.error(f"[FashionSigLIP] classify_all_attributes hatası: {exc}")
            return {"success": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Singleton & startup helper
# ---------------------------------------------------------------------------

classifier = FashionClassifier()


def load_model_on_startup() -> None:
    """main.py lifespan'ından çağrılır. Model başlatma sırasında yüklenir."""
    classifier.load()
