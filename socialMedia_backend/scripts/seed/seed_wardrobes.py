import random
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wardrobe import Color, Style, Subcategory, WardrobeItem


def generate_wardrobes(db: Session, users: list):
    print("[Seed] Gardıroplar üretiliyor...")
    
    subcategories = db.execute(select(Subcategory)).scalars().all()
    colors = db.execute(select(Color)).scalars().all()
    styles = db.execute(select(Style)).scalars().all()
    
    if not subcategories or not colors or not styles:
        print("[Seed] HATA: Referans verileri (kategori, renk, stil) bulunamadı.")
        return
        
    wardrobe_items = []
    
    for user in users:
        role = getattr(user, "_seed_role", "casual")
        
        if role == "influencer":
            count = random.randint(150, 300)
        elif role == "active":
            count = random.randint(80, 200)
        elif role == "casual":
            count = random.randint(20, 50)
        elif role == "new":
            count = random.randint(5, 15)
        else:
            count = 0  # silent
            
        for _ in range(count):
            subcat = random.choice(subcategories)
            color = random.choice(colors)
            style = random.choice(styles)
            
            # 60% chance to have an image, otherwise none (just for realism, but UI might need images)
            # Let's provide mock images for all to look good in the UI
            cat_name = subcat.category.name if subcat.category else "Other"
            image_url = f"https://source.unsplash.com/400x400/?{cat_name.replace(' ', ',')},{color.name}"
            
            item = WardrobeItem(
                id=uuid.uuid4(),
                user_id=user.id,
                subcategory_id=subcat.id,
                primary_color_id=color.id,
                brand=random.choice(["Zara", "H&M", "Nike", "Adidas", "Mango", "Puma", "Uniqlo", "Gucci", None]),
                storage_path=image_url,
                favorite=random.random() > 0.8,
                wear_count=random.randint(0, 50),
            )
            # Add to many-to-many relationship later or just use the model directly if we had a wardrobe_item_styles table
            chosen_styles = random.sample(styles, k=random.randint(1, 2))
            for s in chosen_styles:
                item.styles.append(s)
                
            wardrobe_items.append(item)
            
    # Can't use bulk_save_objects easily with many-to-many relationships (item.styles) in a single pass without extra work
    # We will use db.add_all instead
    
    batch_size = 5000
    for i in range(0, len(wardrobe_items), batch_size):
        db.add_all(wardrobe_items[i:i+batch_size])
        db.commit()
        print(f"[Seed] {i+len(wardrobe_items[i:i+batch_size])} / {len(wardrobe_items)} kıyafet kaydedildi.")

    print(f"[Seed] Toplam {len(wardrobe_items)} kıyafet başarıyla eklendi.")
    return wardrobe_items
