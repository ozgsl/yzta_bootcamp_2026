import logging

from sqlalchemy.orm import Session

from app.models.social import Like
from app.repositories.post_repository import PostRepository
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class LikeService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.post_repo = PostRepository(db)

    def like_post(self, user_id: str, post_id: str) -> bool:
        """
        Likes a post and triggers a notification.
        Returns True if successful, False if already liked.
        Raises ValueError if post not found.
        """
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise ValueError("Post bulunamadı.")
            
        existing = self.db.query(Like).filter(
            Like.post_id == post_id, 
            Like.user_id == user_id
        ).first()
        
        if existing:
            return False # Already liked
            
        new_like = Like(post_id=post_id, user_id=user_id)
        self.db.add(new_like)
        
        if post.likes_count is not None:
            post.likes_count += 1
            
        self.db.commit()
        
        # Trigger Notification if liking someone else's post
        if str(post.user_id) != user_id:
            try:
                self.notification_service.create_notification(
                    actor_id=user_id,
                    target_user_id=str(post.user_id),
                    notif_type="like",
                    post_id=post_id
                )
            except Exception as e:
                logger.error(f"Like bildirimi oluşturulurken hata: {e}")
                
        return True

    def unlike_post(self, user_id: str, post_id: str) -> bool:
        """
        Unlikes a post.
        Returns True if successful, False if like did not exist.
        Raises ValueError if post not found.
        """
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise ValueError("Post bulunamadı.")
            
        existing = self.db.query(Like).filter(
            Like.post_id == post_id, 
            Like.user_id == user_id
        ).first()
        
        if not existing:
            return False
            
        self.db.delete(existing)
        
        if post.likes_count is not None and post.likes_count > 0:
            post.likes_count -= 1
            
        self.db.commit()
        return True
