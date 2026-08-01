from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wardrobe import (
    Category,
    Color,
    Season,
    Style,
    Subcategory,
    WardrobeItem,
    WardrobeItemStyle,
)

CLOTH_FIELDS = [
    "tur", "renk", "renk_hex", "renk_kategori_id", "marka", "beden", "kumas", "kesim", "yaka_tipi",
    "kol_tipi", "desen", "mevsim", "stil_etiketi", "kullanim_sikligi",
    "kombin_notu", "temiz", "foto_url", "is_favorite",
]

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------- Categories ----------
    def get_categories(self) -> dict[str, list[str]]:
        # This will return existing data dynamically or mock structure based on what's populated
        result = {
            "tur": [c.name for c in self.db.scalars(select(Subcategory)).all()],
            "renk": [c.name for c in self.db.scalars(select(Color)).all()],
            "stil_etiketi": [s.name for s in self.db.scalars(select(Style)).all()],
            "mevsim": [s.name for s in self.db.scalars(select(Season)).all()],
        }
        return result

    # ---------- Clothes / Items ----------
    def _get_or_create_subcategory(self, name: str) -> str:
        if not name:
            return None
        sub = self.db.scalars(select(Subcategory).where(Subcategory.name == name)).first()
        if not sub:
            # Fallback to a default category if not exists
            cat = self.db.scalars(select(Category).where(Category.name == "Genel")).first()
            if not cat:
                cat = Category(name="Genel")
                self.db.add(cat)
                self.db.commit()
            sub = Subcategory(name=name, category_id=cat.id)
            self.db.add(sub)
            self.db.commit()
        return str(sub.id)

    def _get_or_create_color(self, name: str, hex_code: str = None) -> str:
        if not name:
            return None
        color = self.db.scalars(select(Color).where(Color.name == name)).first()
        if not color:
            color = Color(name=name, hex_code=hex_code)
            self.db.add(color)
            self.db.commit()
        return str(color.id)

    def add_cloth(self, user_id: str, **fields) -> str:
        # Resolve related fields
        subcat_id = self._get_or_create_subcategory(fields.get("tur"))
        color_id = self._get_or_create_color(fields.get("renk"), fields.get("renk_hex"))
        
        item = WardrobeItem(
            user_id=user_id,
            subcategory_id=subcat_id,
            primary_color_id=color_id,
            brand=fields.get("marka"),
            size=fields.get("beden"),
            is_clean=fields.get("temiz", True),
            notes=fields.get("kombin_notu"),
            favorite=fields.get("is_favorite", False),
            storage_path=fields.get("foto_url")
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        
        # Link style if provided
        if fields.get("stil_etiketi"):
            style = self.db.scalars(select(Style).where(Style.name == fields.get("stil_etiketi"))).first()
            if not style:
                style = Style(name=fields.get("stil_etiketi"))
                self.db.add(style)
                self.db.commit()
            
            link = WardrobeItemStyle(item_id=item.id, style_id=style.id)
            self.db.add(link)
            self.db.commit()

        return str(item.id)

    def _map_item_to_dict(self, item: WardrobeItem) -> dict:
        return {
            "id": str(item.id),
            "user_id": str(item.user_id),
            "tur": item.subcategory.name if item.subcategory else None,
            "renk": item.primary_color.name if item.primary_color else None,
            "renk_hex": item.primary_color.hex_code if item.primary_color else None,
            "marka": item.brand,
            "beden": item.size,
            "temiz": item.is_clean,
            "is_favorite": item.favorite,
            "foto_url": item.storage_path,
            "kombin_notu": item.notes,
            "stil_etiketi": item.styles[0].name if item.styles else None,
            "mevsim": item.seasons[0].name if item.seasons else None,
        }

    def get_clothes(self, user_id: str, clean_only: bool = False) -> list[dict]:
        query = select(WardrobeItem).where(WardrobeItem.user_id == user_id)
        if clean_only:
            query = query.where(WardrobeItem.is_clean == True)
        
        items = self.db.scalars(query.order_by(WardrobeItem.created_at.desc())).all()
        return [self._map_item_to_dict(item) for item in items]

    def get_cloth(self, item_id: str) -> dict | None:
        item = self.db.scalars(select(WardrobeItem).where(WardrobeItem.id == item_id)).first()
        if not item:
            return None
        return self._map_item_to_dict(item)

    def update_cloth(self, item_id: str, **fields) -> bool:
        item = self.db.scalars(select(WardrobeItem).where(WardrobeItem.id == item_id)).first()
        if not item:
            return False

        if "temiz" in fields:
            item.is_clean = fields["temiz"]
        if "is_favorite" in fields:
            item.favorite = fields["is_favorite"]
        if "marka" in fields:
            item.brand = fields["marka"]
        if "beden" in fields:
            item.size = fields["beden"]
        if "kombin_notu" in fields:
            item.notes = fields["kombin_notu"]
        if "foto_url" in fields:
            item.storage_path = fields["foto_url"]
            
        self.db.commit()
        return True

    def delete_cloth(self, item_id: str) -> bool:
        item = self.db.scalars(select(WardrobeItem).where(WardrobeItem.id == item_id)).first()
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True

