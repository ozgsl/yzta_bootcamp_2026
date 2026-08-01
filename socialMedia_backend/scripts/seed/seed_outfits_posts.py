import random
import uuid

from faker import Faker
from sqlalchemy.orm import Session

from app.models.outfit import Outfit, OutfitItem
from app.models.social import Post

fake = Faker()

def generate_outfits_and_posts(db: Session, users: list, wardrobe_items: list):
    print("[Seed] Kombinler ve Gönderiler (Posts) üretiliyor...")
    
    # Group wardrobe items by user
    user_items = {}
    for item in wardrobe_items:
        if item.user_id not in user_items:
            user_items[item.user_id] = []
        user_items[item.user_id].append(item)
        
    outfits = []
    outfit_items = []
    posts = []
    
    for user in users:
        role = getattr(user, "_seed_role", "casual")
        items = user_items.get(user.id, [])
        
        if not items:
            continue
            
        if role == "influencer":
            outfit_count = random.randint(30, 80)
        elif role == "active":
            outfit_count = random.randint(15, 30)
        elif role == "casual":
            outfit_count = random.randint(3, 10)
        elif role == "new":
            outfit_count = random.randint(0, 2)
        else:
            outfit_count = 0
            
        for _ in range(outfit_count):
            # Pick 2 to 5 random items for an outfit
            selected_items = random.sample(items, min(len(items), random.randint(2, 5)))
            
            outfit = Outfit(
                id=uuid.uuid4(),
                user_id=user.id,
                description=fake.sentence(),
                context_json='{"season": "all"}'
            )
            outfits.append(outfit)
            
            for item in selected_items:
                oi = OutfitItem(outfit_id=outfit.id, item_id=item.id)
                outfit_items.append(oi)
                
            # Create a post for this outfit (about 80% of outfits get posted)
            if random.random() > 0.2:
                post = Post(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    image_url=selected_items[0].storage_path if selected_items else None,
                    content=fake.text(max_nb_chars=150) + " #OOTD #Fashion",
                    outfit_id=outfit.id,
                    visibility="public",
                    likes_count=0
                )
                posts.append(post)
                
    # Bulk insert
    db.bulk_save_objects(outfits)
    db.bulk_save_objects(outfit_items)
    db.bulk_save_objects(posts)
    db.commit()
    
    print(f"[Seed] {len(outfits)} Kombin ve {len(posts)} Gönderi eklendi.")
    return posts
