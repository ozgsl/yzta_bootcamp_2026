import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.social import Notification
from app.services.notifications.channels import (
    EmailChannel,
    InAppChannel,
    NotificationChannel,
    PushChannel,
    WebSocketChannel,
)

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Handles notifications across multiple channels.
    """
    def __init__(self, db: Session, channels: list[NotificationChannel] = None):
        self.db = db
        # By default, use In-App, Email and Push. (In production, these could be configurable per user)
        self.channels = channels or [InAppChannel(), EmailChannel(), PushChannel(), WebSocketChannel()]

    def _broadcast(self, user_id: str, payload: dict):
        for channel in self.channels:
            try:
                channel.send(user_id=user_id, payload=payload, db=self.db)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.__class__.__name__}: {e!s}")

    def create_like_notification(self, actor_id: str, target_user_id: str, post_id: str):
        if actor_id == target_user_id:
            return
            
        payload = {
            "actor_id": actor_id,
            "type": "like",
            "post_id": post_id,
            "comment_id": None
        }
        self._broadcast(target_user_id, payload)

    def create_comment_notification(self, actor_id: str, target_user_id: str, post_id: str, comment_id: str):
        if actor_id == target_user_id:
            return
            
        payload = {
            "actor_id": actor_id,
            "type": "comment",
            "post_id": post_id,
            "comment_id": comment_id
        }
        self._broadcast(target_user_id, payload)

    def create_follow_notification(self, actor_id: str, target_user_id: str):
        if actor_id == target_user_id:
            return
            
        payload = {
            "actor_id": actor_id,
            "type": "follow",
            "post_id": None,
            "comment_id": None
        }
        self._broadcast(target_user_id, payload)

    def get_unread_notifications(self, user_id: str):
        return self.db.scalars(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .order_by(Notification.created_at.desc())
        ).all()

    def mark_as_read(self, notification_id: str):
        notif = self.db.scalars(select(Notification).where(Notification.id == notification_id)).first()
        if notif:
            notif.is_read = True
            self.db.commit()
