from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.social import Post, Profile
from app.models.wardrobe import WardrobeItem


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_wardrobe_stats(self, user_id: str) -> dict:
        total_items = self.db.scalars(
            select(func.count(WardrobeItem.id)).where(WardrobeItem.user_id == user_id)
        ).first() or 0
        
        # Color stats
        # Assuming WardrobeItem has a color field (maybe string or relationship)
        # We will mock the aggregation if the DB structure is complex, or use direct SQL
        return {
            "toplam_kiyafet": total_items,
            "renk_dagilimi": [], # to be implemented with group_by
            "kategori_dagilimi": [] # to be implemented with group_by
        }

    def get_engagement_stats(self, user_id: str) -> dict:
        total_likes = self.db.scalars(
            select(func.sum(Post.likes_count)).where(Post.user_id == user_id)
        ).first() or 0
        
        total_posts = self.db.scalars(
            select(func.count(Post.id)).where(Post.user_id == user_id)
        ).first() or 0
        
        user = self.db.scalars(select(Profile).where(Profile.id == user_id)).first()
        followers = user.followers_count if user else 0
        
        return {
            "toplam_begeni": total_likes,
            "toplam_post": total_posts,
            "takipci": followers
        }

    def get_achievements(self, user_id: str) -> list:
        stats = self.get_engagement_stats(user_id)
        w_stats = self.get_wardrobe_stats(user_id)
        
        achievements = []
        if w_stats["toplam_kiyafet"] > 10:
            achievements.append({"name": "Moda İkonu Başlangıcı", "description": "Dolabında 10'dan fazla ürün var."})
        if stats["toplam_begeni"] > 100:
            achievements.append({"name": "Fenomen", "description": "Toplam 100 beğeni aldın."})
            
        return achievements
