import logging
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wardrobe import Color, Style, Subcategory, WardrobeItem

# Cloud Run ortamında PyTorch yüklemesini atla
_fashion_classifier = None

def _get_classifier():
    global _fashion_classifier
    if _fashion_classifier is None and "K_SERVICE" not in os.environ:
        from app.services import fashion_classifier as _fc
        _fashion_classifier = _fc
    return _fashion_classifier

logger = logging.getLogger(__name__)

class WardrobeService:
    """
    Handles Wardrobe business logic: CRUD, AI Classification, Color Normalization, Duplicate Checks.
    """
    def __init__(self, db: Session):
        self.db = db
        self.fashion_classifier = _get_classifier()

    def process_and_add_item(self, user_id: str, filename: str) -> WardrobeItem:
        """
        Takes an uploaded image filename, runs AI classification, and creates a WardrobeItem.
        """
        # Resolve local path
        local_path = Path("uploads") / filename
        if not local_path.exists():
            local_path = Path("static/uploads") / filename
            
        if not local_path.exists():
            raise FileNotFoundError("Yüklenen dosya bulunamadı.")
            
        # 1. AI Sınıflandırması
        ai_result = self.fashion_classifier.classify_image(image_path=local_path)
        if not ai_result.get("success"):
            raise RuntimeError(f"AI model hatası: {ai_result.get('error', 'Bilinmeyen hata')}")
            
        pred = ai_result.get("predictions", {})
        
        # 2. Attribute Eşleştirme (Kategori, Renk, Stil vb.)
        cat_name = pred.get("category")
        color_name = pred.get("color")
        style_name = pred.get("style")
        
        # Lookups
        subcategory = self.db.scalars(select(Subcategory).where(Subcategory.name == cat_name)).first()
        color = self.db.scalars(select(Color).where(Color.name == color_name)).first()
        
        # 3. Duplicate Kontrolü
        # (İleri seviyede görüntü hash'i veya feature vector karşılaştırması yapılabilir)
        existing = self.db.scalars(
            select(WardrobeItem).where(
                WardrobeItem.user_id == user_id,
                WardrobeItem.storage_path == f"uploads/{filename}"
            )
        ).first()
        if existing:
            raise ValueError("Bu kıyafet zaten gardırobunuzda var.")
            
        # 4. Veritabanına Ekleme
        new_item = WardrobeItem(
            user_id=user_id,
            storage_path=f"uploads/{filename}",
            subcategory_id=subcategory.id if subcategory else None,
            primary_color_id=color.id if color else None,
            # AI predictions can be dumped into notes for now
            notes=f"AI Tahminleri: Kategori: {cat_name}, Renk: {color_name}, Stil: {style_name}"
        )
        
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        
        # If style exists, attach it
        if style_name:
            style = self.db.scalars(select(Style).where(Style.name == style_name)).first()
            if style:
                new_item.styles.append(style)
                self.db.commit()
                
        return new_item

    def get_user_items(self, user_id: str):
        return self.db.scalars(
            select(WardrobeItem).where(WardrobeItem.user_id == user_id)
        ).all()

    def update_item(self, item_id: str, user_id: str, updates: dict):
        item = self.db.scalars(select(WardrobeItem).where(WardrobeItem.id == item_id)).first()
        if not item:
            raise ValueError("Kıyafet bulunamadı.")
        if str(item.user_id) != user_id:
            raise PermissionError("Bu kıyafeti güncelleme yetkiniz yok.")
            
        for key, value in updates.items():
            setattr(item, key, value)
            
        self.db.commit()

    def delete_item(self, item_id: str, user_id: str):
        item = self.db.scalars(select(WardrobeItem).where(WardrobeItem.id == item_id)).first()
        if not item:
            raise ValueError("Kıyafet bulunamadı.")
        if str(item.user_id) != user_id:
            raise PermissionError("Bu kıyafeti silme yetkiniz yok.")
            
        self.db.delete(item)
        self.db.commit()

    def set_laundry_status(self, item_id: str, user_id: str, is_dirty: bool):
        self.update_item(item_id, user_id, {"is_dirty": is_dirty})

    def set_favorite_status(self, item_id: str, user_id: str, is_favorite: bool):
        self.update_item(item_id, user_id, {"is_favorite": is_favorite})

    def analyze_image(self, image_url: str) -> dict:
        from app.services.providers.ai_provider import OllamaProvider
        ai_provider = OllamaProvider()
        
        # Determine if URL is local path or remote URL
        if image_url.startswith("http://") or image_url.startswith("https://"):
            # Normally we would download or pass URL. For mock:
            import base64

            import httpx
            with httpx.Client(timeout=15.0) as c:
                r = c.get(image_url)
                r.raise_for_status()
            image_b64 = base64.b64encode(r.content).decode()
            return ai_provider.classify_image(image_b64=image_b64)
        else:
            return ai_provider.classify_image(image_path=image_url)

    def chat_with_stylist(self, user_id: str, message: str, weather: str = None) -> dict:
        from app.services.providers.ai_provider import OllamaProvider
        ai_provider = OllamaProvider()
        
        # Here we should fetch chat history from DB instead of ItemRepository.
        # But we haven't created ChatMessage model yet. Assuming it's in ItemRepository for now,
        # or we can mock it empty.
        history = []
        
        context_message = message
        if weather:
            context_message = f"[System Note: Current weather is '{weather}']\nUser: {message}"
            
        return ai_provider.get_chat_response(history, context_message)
