"""
Notifications Router — Bildirim sistemi.

Endpoints:
  GET    /notifications?user_id=...              - Bildirimleri listele
  PUT    /notifications/{notification_id}/read    - Bildirimi okundu işaretle
  PUT    /notifications/read-all?user_id=...      - Tüm bildirimleri okundu işaretle
  GET    /notifications/unread-count?user_id=...  - Okunmamış bildirim sayısı
"""
from __future__ import annotations

import sqlite3
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.core.database import get_db
from app.domain.schemas import MessageResponse

router = APIRouter()


def create_notification(
    db: sqlite3.Connection,
    user_id: str,
    actor_id: str,
    notif_type: str,
    post_id: Optional[str] = None,
    comment_id: Optional[str] = None,
):
    """Yardımcı fonksiyon: bildirim oluşturur. Kendi kendine bildirim göndermez."""
    if user_id == actor_id:
        return  # Kendi aksiyonun için bildirim gönderme
    notification_id = f"notif-{uuid.uuid4().hex[:12]}"
    db.execute(
        "INSERT INTO notifications (notification_id, user_id, actor_id, type, post_id, comment_id) VALUES (?,?,?,?,?,?)",
        (notification_id, user_id, actor_id, notif_type, post_id, comment_id),
    )


@router.get("/")
@router.get("")
def get_notifications(
    user_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    db: sqlite3.Connection = Depends(get_db),
):
    """Kullanıcının bildirimlerini listeler."""
    try:
        rows = db.execute(
            """SELECT n.notification_id, n.user_id, n.actor_id, n.type, n.post_id,
                      n.comment_id, n.is_read, n.created_at,
                      u.username AS actor_username,
                      u.display_name AS actor_display_name,
                      u.avatar_url AS actor_avatar_url,
                      p.image_url AS post_image_url
               FROM notifications n
               JOIN users u ON n.actor_id = u.user_id
               LEFT JOIN posts p ON n.post_id = p.post_id
               WHERE n.user_id = ?
               ORDER BY n.created_at DESC
               LIMIT ?""",
            (user_id, limit),
        ).fetchall()

        notifications = []
        for r in rows:
            notif_type = r["type"]
            # Türkçe bildirim mesajları oluştur
            actor_name = r["actor_display_name"] or r["actor_username"]
            if notif_type == "like":
                message = f"{actor_name} gönderini beğendi"
            elif notif_type == "comment":
                message = f"{actor_name} gönderine yorum yaptı"
            elif notif_type == "follow":
                message = f"{actor_name} seni takip etmeye başladı"
            elif notif_type == "mention":
                message = f"{actor_name} seni bir gönderide etiketledi"
            else:
                message = f"{actor_name} bir bildirim gönderdi"

            notifications.append({
                "notification_id": r["notification_id"],
                "user_id": r["user_id"],
                "actor_id": r["actor_id"],
                "actor_username": r["actor_username"],
                "actor_display_name": r["actor_display_name"],
                "actor_avatar_url": r["actor_avatar_url"],
                "type": notif_type,
                "message": message,
                "post_id": r["post_id"],
                "post_image_url": r["post_image_url"],
                "comment_id": r["comment_id"],
                "is_read": bool(r["is_read"]),
                "created_at": r["created_at"],
            })

        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bildirimler alınırken hata: {e}")


@router.get("/unread-count")
def get_unread_count(
    user_id: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
):
    """Okunmamış bildirim sayısını döndürür."""
    try:
        row = db.execute(
            "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND is_read = 0",
            (user_id,),
        ).fetchone()
        return {"count": row["cnt"] if row else 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}/read", response_model=MessageResponse)
def mark_as_read(
    notification_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    """Tek bir bildirimi okundu işaretler."""
    try:
        db.execute(
            "UPDATE notifications SET is_read = 1 WHERE notification_id = ?",
            (notification_id,),
        )
        db.commit()
        return MessageResponse(success=True, message="Bildirim okundu olarak işaretlendi")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/read-all", response_model=MessageResponse)
def mark_all_as_read(
    user_id: str = Query(...),
    db: sqlite3.Connection = Depends(get_db),
):
    """Kullanıcının tüm bildirimlerini okundu işaretler."""
    try:
        db.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = ? AND is_read = 0",
            (user_id,),
        )
        db.commit()
        return MessageResponse(success=True, message="Tüm bildirimler okundu olarak işaretlendi")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
