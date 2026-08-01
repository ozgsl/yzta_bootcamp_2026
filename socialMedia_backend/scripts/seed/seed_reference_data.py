from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wardrobe import Category, Color, Style, Subcategory


def seed_categories(db: Session):
    print("[Seed] Kategoriler yükleniyor...")
    categories_data = {
        "Üst Giyim": ["T-Shirt", "Gömlek", "Kazak", "Sweatshirt", "Bluz", "Ceket", "Mont", "Yelek", "Kaban"],
        "Alt Giyim": ["Pantolon", "Jean", "Şort", "Etek", "Eşofman Altı"],
        "Dış Giyim": ["Palto", "Kaban", "Yağmurluk", "Trençkot", "Ceket"],
        "Elbise": ["Günlük Elbise", "Abiye", "Tulum"],
        "Ayakkabı": ["Sneaker", "Bot", "Çizme", "Topuklu Ayakkabı", "Sandalet", "Terlik", "Klasik Ayakkabı"],
        "Çanta": ["Sırt Çantası", "Omuz Çantası", "El Çantası", "Çapraz Çanta", "Bez Çanta"],
        "Aksesuar": ["Şapka", "Bere", "Atkı", "Eldiven", "Kemer", "Güneş Gözlüğü", "Saat", "Takı", "Eşarp", "Şal"]
    }
    
    for cat_name, subcats in categories_data.items():
        cat = db.scalars(select(Category).where(Category.name == cat_name)).first()
        if not cat:
            cat = Category(name=cat_name)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            
        for sub_name in subcats:
            sub = db.scalars(select(Subcategory).where(Subcategory.name == sub_name, Subcategory.category_id == cat.id)).first()
            if not sub:
                sub = Subcategory(name=sub_name, category_id=cat.id)
                db.add(sub)
    db.commit()


def seed_colors(db: Session):
    print("[Seed] Renkler yükleniyor...")
    colors_data = [
        {"name": "Siyah", "hex_code": "#000000", "family": "Neutral", "brightness": "Dark"},
        {"name": "Beyaz", "hex_code": "#FFFFFF", "family": "Neutral", "brightness": "Light"},
        {"name": "Gri", "hex_code": "#808080", "family": "Neutral", "brightness": "Medium"},
        {"name": "Lacivert", "hex_code": "#000080", "family": "Blue", "brightness": "Dark"},
        {"name": "Mavi", "hex_code": "#0000FF", "family": "Blue", "brightness": "Medium"},
        {"name": "Açık Mavi", "hex_code": "#ADD8E6", "family": "Blue", "brightness": "Light"},
        {"name": "Kırmızı", "hex_code": "#FF0000", "family": "Red", "brightness": "Medium"},
        {"name": "Bordo", "hex_code": "#800000", "family": "Red", "brightness": "Dark"},
        {"name": "Pembe", "hex_code": "#FFC0CB", "family": "Pink", "brightness": "Light"},
        {"name": "Yeşil", "hex_code": "#008000", "family": "Green", "brightness": "Medium"},
        {"name": "Haki", "hex_code": "#BDB76B", "family": "Green", "brightness": "Medium"},
        {"name": "Zeytin Yeşili", "hex_code": "#808000", "family": "Green", "brightness": "Dark"},
        {"name": "Sarı", "hex_code": "#FFFF00", "family": "Yellow", "brightness": "Light"},
        {"name": "Hardal", "hex_code": "#FFDB58", "family": "Yellow", "brightness": "Medium"},
        {"name": "Turuncu", "hex_code": "#FFA500", "family": "Orange", "brightness": "Medium"},
        {"name": "Kahverengi", "hex_code": "#A52A2A", "family": "Brown", "brightness": "Dark"},
        {"name": "Bej", "hex_code": "#F5F5DC", "family": "Brown", "brightness": "Light"},
        {"name": "Krem", "hex_code": "#FFFDD0", "family": "Neutral", "brightness": "Light"},
        {"name": "Mor", "hex_code": "#800080", "family": "Purple", "brightness": "Dark"},
        {"name": "Lila", "hex_code": "#C8A2C8", "family": "Purple", "brightness": "Light"},
    ]
    
    for c in colors_data:
        color = db.scalars(select(Color).where(Color.name == c["name"])).first()
        if not color:
            color = Color(**c)
            db.add(color)
    db.commit()


def seed_styles(db: Session):
    print("[Seed] Stiller yükleniyor...")
    styles_data = [
        "Casual", "Streetwear", "Minimal", "Old Money", "Vintage",
        "Sporty", "Business", "Bohemian", "Gothic", "Preppy", "Chic",
        "Modest", "Y2K", "Techwear", "Avant-Garde"
    ]
    
    for s_name in styles_data:
        style = db.scalars(select(Style).where(Style.name == s_name)).first()
        if not style:
            style = Style(name=s_name)
            db.add(style)
    db.commit()


def seed_reference_data(db: Session):
    """Tüm referans verileri veritabanına ekler."""
    seed_categories(db)
    seed_colors(db)
    seed_styles(db)
    print("[Seed] Referans verileri başarıyla yüklendi.")
