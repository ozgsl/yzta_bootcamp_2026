from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session

from app.models.social import Notification


class NotificationChannel(ABC):
    @abstractmethod
    def send(self, user_id: str, payload: dict[str, Any], db: Session) -> bool:
        """Sends a notification through this channel."""

class InAppChannel(NotificationChannel):
    """Stores notification in the database for the in-app feed."""
    def send(self, user_id: str, payload: dict[str, Any], db: Session) -> bool:
        notif = Notification(
            user_id=user_id,
            actor_id=payload.get("actor_id"),
            type=payload.get("type"),
            post_id=payload.get("post_id"),
            comment_id=payload.get("comment_id")
        )
        db.add(notif)
        db.commit()
        return True

class EmailChannel(NotificationChannel):
    """Sends an email notification."""
    def send(self, user_id: str, payload: dict[str, Any], db: Session) -> bool:
        # TODO: Implement actual SMTP/SendGrid logic here.
        # Requires fetching user email from db using user_id
        print(f"[EMAIL MOCK] Sent to User: {user_id} | Payload: {payload}")
        return True

class PushChannel(NotificationChannel):
    """Sends a mobile push notification (e.g. Firebase Cloud Messaging)."""
    def send(self, user_id: str, payload: dict[str, Any], db: Session) -> bool:
        # TODO: Implement FCM logic here.
        print(f"[PUSH MOCK] Sent to User: {user_id} | Payload: {payload}")
        return True

class WebSocketChannel(NotificationChannel):
    """Sends real-time notification over WebSockets."""
    def send(self, user_id: str, payload: dict[str, Any], db: Session) -> bool:
        # TODO: Implement WebSocket broadcast here.
        print(f"[WS MOCK] Sent to User: {user_id} | Payload: {payload}")
        return True
