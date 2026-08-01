import random

from faker import Faker
from sqlalchemy.orm import Session

from app.models.social import Comment, Follow, Like, Post

fake = Faker()

def generate_social_graph_and_interactions(db: Session, users: list, posts: list):
    print("[Seed] Sosyal Etkileşimler (Takip, Beğeni, Yorum) üretiliyor...")
    
    # 1. Follows
    # Influencer users get a lot of followers
    influencers = [u for u in users if getattr(u, "_seed_role", "") == "influencer"]
    others = [u for u in users if getattr(u, "_seed_role", "") != "influencer"]
    
    follows = []
    
    for user in others:
        # Everyone follows a few influencers
        follow_count = random.randint(3, 10)
        selected_influencers = random.sample(influencers, min(follow_count, len(influencers)))
        for inf in selected_influencers:
            follows.append(Follow(follower_id=user.id, following_id=inf.id))
            
        # Also follow some random others
        random_count = random.randint(1, 15)
        selected_others = random.sample(others, min(random_count, len(others)))
        for other in selected_others:
            if other.id != user.id:
                follows.append(Follow(follower_id=user.id, following_id=other.id))
                
    # Bulk insert follows, ignoring duplicates requires more care, but sample makes it mostly safe
    # Filter exact duplicates just in case
    unique_follows = {}
    for f in follows:
        unique_follows[(f.follower_id, f.following_id)] = f
    
    db.bulk_save_objects(list(unique_follows.values()))
    db.commit()
    print(f"[Seed] {len(unique_follows)} Takip ilişkisi eklendi.")
    
    # 2. Likes & Comments
    likes = []
    comments = []
    
    # We want to increment post likes_count accurately
    post_likes_map = {post.id: 0 for post in posts}
    
    for post in posts:
        # Determine popularity based on user role roughly
        post_owner = next((u for u in users if u.id == post.user_id), None)
        role = getattr(post_owner, "_seed_role", "casual") if post_owner else "casual"
        
        if role == "influencer":
            like_count = random.randint(50, 150)
            comment_count = random.randint(5, 20)
        elif role == "active":
            like_count = random.randint(10, 40)
            comment_count = random.randint(1, 5)
        else:
            like_count = random.randint(0, 15)
            comment_count = random.randint(0, 2)
            
        # Add likes
        likers = random.sample(users, min(like_count, len(users)))
        for liker in likers:
            likes.append(Like(post_id=post.id, user_id=liker.id))
            post_likes_map[post.id] += 1
            
        # Add comments
        commenters = random.sample(users, min(comment_count, len(users)))
        for commenter in commenters:
            comments.append(Comment(
                post_id=post.id,
                user_id=commenter.id,
                content=random.choice([
                    "Çok güzel görünüyor!",
                    "Bu kombine bayıldım 😍",
                    "Harika uyum!",
                    "Nereden aldın?",
                    "Tarzın çok iyi.",
                    "İlham verici! 🔥",
                    fake.sentence()
                ])
            ))

    db.bulk_save_objects(likes)
    db.bulk_save_objects(comments)
    db.commit()
    
    # Update likes_count in DB
    for post_id, l_count in post_likes_map.items():
        if l_count > 0:
            p = db.query(Post).filter(Post.id == post_id).first()
            if p:
                p.likes_count = l_count
    db.commit()
    
    print(f"[Seed] {len(likes)} Beğeni ve {len(comments)} Yorum eklendi.")
