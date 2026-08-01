import argparse
import os
import random

# Add parent directory to path so we can import app
import sys
import time

from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models.base import Base, engine
from app.models.outfit import *
from app.models.social import *
from app.models.wardrobe import *
from scripts.seed.seed_outfits_posts import generate_outfits_and_posts
from scripts.seed.seed_reference_data import seed_reference_data
from scripts.seed.seed_social import generate_social_graph_and_interactions
from scripts.seed.seed_users import generate_users
from scripts.seed.seed_wardrobes import generate_wardrobes


def clean_database(db: Session):
    print("[Seed] Veritabanı temizleniyor...")
    # Sadece Drop and Create all
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("[Seed] Veritabanı sıfırlandı.")

def main():
    parser = argparse.ArgumentParser(description="Dijital Gardrop Seed Script")
    parser.add_argument("--profile", choices=["dev", "demo", "production"], default="dev", 
                        help="Seed profile (dev: 30 users, demo: 250 users, prod: 1000 users)")
    args = parser.parse_args()
    
    if args.profile == "dev":
        total_users = 30
    elif args.profile == "demo":
        total_users = 250
    else:
        total_users = 1000

    # Ensure determinism for seed
    SEED = 42
    random.seed(SEED)
    
    start_time = time.time()
    
    with Session(engine) as db:
        clean_database(db)
        
        # 1. Reference Data
        seed_reference_data(db)
        
        # 2. Users
        users = generate_users(db, total_users)
        
        # 3. Wardrobes
        wardrobe_items = generate_wardrobes(db, users)
        
        # 4. Outfits and Posts
        posts = generate_outfits_and_posts(db, users, wardrobe_items)
        
        # 5. Social Graph
        generate_social_graph_and_interactions(db, users, posts)
        
    duration = time.time() - start_time
    print("========================================")
    print(f"✅ Seed işlemi başarıyla tamamlandı! ({args.profile.upper()} Profili)")
    print(f"⏱️ Süre: {duration:.2f} saniye")
    print(f"👥 Toplam Kullanıcı: {total_users}")
    if wardrobe_items:
        print(f"👕 Toplam Kıyafet: {len(wardrobe_items)}")
    if posts:
        print(f"📸 Toplam Post: {len(posts)}")
    print("========================================")

if __name__ == "__main__":
    main()
