import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.social import Follow
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class FollowService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.user_repo = UserRepository(db)

    def follow_user(self, follower_id: str, following_id: str) -> bool:
        if follower_id == following_id:
            raise ValueError("Kullanıcı kendini takip edemez.")
            
        target_user = self.user_repo.get_user_by_id(following_id)
        if not target_user:
            raise ValueError("Takip edilmek istenen kullanıcı bulunamadı.")
            
        existing = self.db.scalars(
            select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
        ).first()
        
        if existing:
            return False # Already following
            
        new_follow = Follow(follower_id=follower_id, following_id=following_id)
        self.db.add(new_follow)
        self.db.commit()
        
        try:
            self.notification_service.create_notification(
                actor_id=follower_id,
                target_user_id=following_id,
                notif_type="follow"
            )
        except Exception as e:
            logger.error(f"Takip bildirimi oluşturulurken hata: {e}")
            
        return True

    def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        existing = self.db.scalars(
            select(Follow).where(Follow.follower_id == follower_id, Follow.following_id == following_id)
        ).first()
        
        if not existing:
            return False
            
        self.db.delete(existing)
        self.db.commit()
        return True

    def get_followers_count(self, user_id: str) -> int:
        return self.db.scalar(select(func.count()).select_from(Follow).where(Follow.following_id == user_id)) or 0

    def get_following_count(self, user_id: str) -> int:
        return self.db.scalar(select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)) or 0
