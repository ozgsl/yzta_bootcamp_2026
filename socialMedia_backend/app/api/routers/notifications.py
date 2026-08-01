from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.services.notification_service import NotificationService

router = APIRouter()

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)

@router.get("/{user_id}")
def get_notifications(
    user_id: str, 
    service: NotificationService = Depends(get_notification_service)
):
    try:
        notifications = service.get_unread_notifications(user_id)
        # Assuming the old formatting happens here or in service. 
        # For simplicity, returning DB objects mapped to JSON.
        result = []
        for n in notifications:
            result.append({
                "id": str(n.id),
                "actor_id": str(n.actor_id) if n.actor_id else None,
                "type": n.type,
                "message": f"Yeni {n.type} bildirimi", # Ideally formatted by actor name
                "post_id": str(n.post_id) if n.post_id else None,
                "comment_id": str(n.comment_id) if n.comment_id else None,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{notification_id}/read")
def mark_as_read(
    notification_id: str, 
    service: NotificationService = Depends(get_notification_service)
):
    try:
        service.mark_as_read(notification_id)
        return {"mesaj": "Bildirim okundu", "message": "Notification read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
