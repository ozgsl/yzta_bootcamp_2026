import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.social import Comment
from app.repositories.post_repository import PostRepository
from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class CommentService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.post_repo = PostRepository(db)

    def add_comment(self, post_id: str, user_id: str, content: str, parent_id: str | None = None) -> Comment:
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise ValueError("Post bulunamadı.")
            
        new_comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id
        )
        self.db.add(new_comment)
        self.db.commit()
        self.db.refresh(new_comment)
        
        # Trigger Notification
        if str(post.user_id) != user_id:
            try:
                self.notification_service.create_notification(
                    actor_id=user_id,
                    target_user_id=str(post.user_id),
                    notif_type="comment",
                    post_id=post_id,
                    comment_id=str(new_comment.id)
                )
            except Exception as e:
                logger.error(f"Yorum bildirimi oluşturulurken hata: {e}")
                
        return new_comment

    def delete_comment(self, comment_id: str, user_id: str):
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise ValueError("Yorum bulunamadı.")
            
        if str(comment.user_id) != user_id:
            raise PermissionError("Bu yorumu silme yetkiniz yok.")
            
        self.db.delete(comment)
        self.db.commit()

    def get_post_comments(self, post_id: str) -> list[Comment]:
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise ValueError("Post bulunamadı.")
            
        comments = self.db.scalars(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.desc())
        ).all()
        return comments
