from __future__ import annotations
import uuid
import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from app.core.database import get_db
from app.api.routers.notifications import create_notification
from app.domain.schemas import PostCreate, PostResponse, OutfitItemResponse, MessageResponse
from app.repositories.post_repository import PostRepository

router = APIRouter()

@router.post("", response_model=MessageResponse, status_code=201)
def create_post(post: PostCreate, db: sqlite3.Connection = Depends(get_db)):
    try:
        return PostRepository.create_post(db, post)
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post(
    post_id: str,
    user_id: str = Query(..., description="Silen kullanıcı ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """Bir gönderiyi siler. Sadece gönderi sahibi silebilir."""
    try:
        row = db.execute("SELECT user_id FROM posts WHERE post_id = ?", (post_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Gönderi bulunamadı")
        if row[0] != user_id:
            raise HTTPException(status_code=403, detail="Bu gönderiyi silme yetkiniz yok")

        # İlişkili kayıtları temizle
        db.execute("DELETE FROM post_outfit_items WHERE post_id = ?", (post_id,))
        db.execute("DELETE FROM likes WHERE post_id = ?", (post_id,))
        try:
            db.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
        except Exception:
            pass  # comments tablosu yoksa geç
        db.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        db.commit()
        return MessageResponse(success=True, message="Gönderi silindi")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

from app.domain.schemas import PostUpdateRequest
@router.patch("/{post_id}", response_model=MessageResponse)
def update_post(
    post_id: str,
    req: PostUpdateRequest,
    user_id: str = Query(..., description="Güncelleyen kullanıcı ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """Bir gönderinin açıklamasını günceller."""
    try:
        row = db.execute("SELECT user_id FROM posts WHERE post_id = ?", (post_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Gönderi bulunamadı")
        if row[0] != user_id:
            raise HTTPException(status_code=403, detail="Bu gönderiyi düzenleme yetkiniz yok")

        if req.caption is not None:
            db.execute("UPDATE posts SET caption = ? WHERE post_id = ?", (req.caption, post_id))
        
        db.commit()
        return MessageResponse(success=True, message="Gönderi güncellendi")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/posts", response_model=List[PostResponse])
def get_user_posts(user_id: str, viewer_id: Optional[str] = Query(None), db: sqlite3.Connection = Depends(get_db)):
    try:
        return PostRepository.get_user_posts(db, user_id, viewer_id)
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@router.get('/users/{user_id}/saved_posts', response_model=List[PostResponse])
def get_saved_posts(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Kullanıcının kaydettiği gönderileri döndürür."""
    try:
        # saved_posts tablosunu oluştur (yoksa)
        db.execute("""
            CREATE TABLE IF NOT EXISTS saved_posts (
                user_id   TEXT NOT NULL,
                post_id   TEXT NOT NULL,
                saved_at  TEXT NOT NULL,
                PRIMARY KEY (user_id, post_id)
            )
        """)
        rows = db.execute("""
            SELECT p.*, u.username, u.display_name, u.avatar_url
            FROM saved_posts sp
            JOIN posts p ON sp.post_id = p.post_id
            JOIN users u ON p.user_id = u.user_id
            WHERE sp.user_id = ?
            ORDER BY sp.saved_at DESC
        """, (user_id,)).fetchall()
        return [] if not rows else [
            PostResponse(
                post_id=r['post_id'], user_id=r['user_id'],
                username=r['username'], display_name=dict(r).get('display_name', ''),
                avatar_url=dict(r).get('avatar_url'), image_url=r['image_url'],
                caption=dict(r).get('caption', ''), visibility=dict(r).get('visibility', 'public'),
                ai_training_consent=bool(dict(r).get('ai_training_consent', 0)),
                likes_count=dict(r).get('likes_count', 0), comments_count=dict(r).get('comments_count', 0),
                is_liked=db.execute(
                    'SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?',
                    (r['post_id'], user_id)
                ).fetchone() is not None,
                is_saved=True,
                outfit_items=[],
                created_at=r['created_at'],
            ) for r in rows
        ]
    except Exception:
        return []


@router.post('/{post_id}/save')
def save_post(post_id: str, user_id: str = Query(...), db: sqlite3.Connection = Depends(get_db)):
    """Gönderiyi kaydeder."""
    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS saved_posts (
                user_id   TEXT NOT NULL,
                post_id   TEXT NOT NULL,
                saved_at  TEXT NOT NULL,
                PRIMARY KEY (user_id, post_id)
            )
        """)
        from datetime import datetime
        saved_at = datetime.utcnow().isoformat()
        db.execute(
            "INSERT OR IGNORE INTO saved_posts (user_id, post_id, saved_at) VALUES (?,?,?)",
            (user_id, post_id, saved_at),
        )
        
        post = db.execute("SELECT user_id FROM posts WHERE post_id = ?", (post_id,)).fetchone()
        if post and post["user_id"] != user_id:
            create_notification(
                db=db,
                user_id=post["user_id"],
                actor_id=user_id,
                notif_type="save",
                post_id=post_id
            )
        
        db.commit()
        return {"success": True, "message": "Kaydedildi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/{post_id}/save')
def unsave_post(post_id: str, user_id: str = Query(...), db: sqlite3.Connection = Depends(get_db)):
    """Gönderiyi kayıtlardan kaldırır."""
    try:
        db.execute(
            "DELETE FROM saved_posts WHERE user_id = ? AND post_id = ?",
            (user_id, post_id)
        )
        db.commit()
        return {"success": True, "message": "Kayıtlardan kaldırıldı"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
