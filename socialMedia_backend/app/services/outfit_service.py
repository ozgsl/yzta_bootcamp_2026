import logging
import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.outfit import Outfit, OutfitItem
from app.models.wardrobe import WardrobeItem

logger = logging.getLogger(__name__)

class OutfitService:
    """
    Handles Outfit generation, AI recommendations, and harmony scoring.
    """
    def __init__(self, db: Session):
        self.db = db

    def generate_random_outfit(self, user_id: str) -> Outfit | None:
        """
        Generates a basic random outfit from user's wardrobe.
        Future: Integrate with AI for weather, event, color/style harmony.
        """
        # Fetch user's items
        items = self.db.scalars(select(WardrobeItem).where(WardrobeItem.user_id == user_id)).all()
        if not items:
            return None
            
        # Basic grouping logic (just a mockup of what the service will do)
        tops = [i for i in items if i.subcategory and i.subcategory.category and i.subcategory.category.name.lower() == "üst giyim"]
        bottoms = [i for i in items if i.subcategory and i.subcategory.category and i.subcategory.category.name.lower() == "alt giyim"]
        shoes = [i for i in items if i.subcategory and i.subcategory.category and i.subcategory.category.name.lower() == "ayakkabı"]
        
        # Fallback if no strict categories
        if not tops: tops = items
        if not bottoms: bottoms = items
        if not shoes: shoes = items
        
        selected_items = [
            random.choice(tops) if tops else None,
            random.choice(bottoms) if bottoms else None,
            random.choice(shoes) if shoes else None
        ]
        
        selected_items = [i for i in selected_items if i is not None]
        
        # Deduplicate
        unique_items = {i.id: i for i in selected_items}.values()
        
        if not unique_items:
            return None

        # Calculate placeholder scores
        color_score = random.randint(70, 100)
        style_score = random.randint(70, 100)
            
        new_outfit = Outfit(
            user_id=user_id,
            description=f"Otomatik Kombin (Renk Uyumu: {color_score}, Stil: {style_score})"
        )
        self.db.add(new_outfit)
        self.db.commit()
        
        # Add Outfit Items
        for item in unique_items:
            oi = OutfitItem(outfit_id=new_outfit.id, item_id=item.id)
            self.db.add(oi)
            
        self.db.commit()
        self.db.refresh(new_outfit)
        return new_outfit

    def generate_ai_outfit(self, user_id: str, weather: str, event_type: str) -> Outfit:
        """
        Future implementation for context-aware AI outfit recommendations.
        """

    def calculate_harmony_score(self, item_ids: list[str]) -> int:
        """
        Calculates color and style harmony for a given set of items.
        """
