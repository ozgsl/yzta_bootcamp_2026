"""
Likes & Comments Router

Endpoints:
  POST   /posts/{post_id}/like              - Beğen
  DELETE /posts/{post_id}/like?user_id=...  - Beğeniyi kaldır
  POST   /posts/{post_id}/comments          - Yorum ekle
  GET    /posts/{post_id}/comments          - Yorumları listele
"""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.domain.schemas import MessageResponse
from app.api.routers.notifications import create_notification

router = APIRouter()


# ─── Like Models ──────────────────────────────────────────────
class LikeRequest(BaseModel):
    user_id: str


# ─── Comment Models ───────────────────────────────────────────
class CommentRequest(BaseModel):
    user_id: str
    content: str
    parent_id: Optional[str] = None


# ══════════════════════════════════════════════════════════════
# LIKES
# ══════════════════════════════════════════════════════════════

@router.post("/posts/{post_id}/like", response_model=MessageResponse, status_code=201)
def like_post(post_id: str, req: LikeRequest, db: sqlite3.Connection = Depends(get_db)):
    """Bir postu beğenir."""
    try:
        post = db.execute("SELECT user_id FROM posts WHERE post_id = ?", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post bulunamadı")

        existing = db.execute(
            "SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?",
            (post_id, req.user_id),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Bu postu zaten beğendiniz")

        db.execute("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", (post_id, req.user_id))
        db.execute("UPDATE posts SET likes_count = likes_count + 1 WHERE post_id = ?", (post_id,))
        
        # Bildirim oluştur
        if post and post[0] != req.user_id:
            create_notification(
                db=db,
                user_id=post[0],
                actor_id=req.user_id,
                notif_type="like",
                post_id=post_id
            )
            
        db.commit()

        return MessageResponse(success=True, message="Beğeni eklendi")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beğeni eklenirken hata: {e}")


@router.delete("/posts/{post_id}/like", response_model=MessageResponse)
def unlike_post(
    post_id: str,
    user_id: str = Query(..., description="Beğeniyi kaldıran kullanıcı ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """Bir postun beğenisini kaldırır. user_id query param olarak alınır."""
    try:
        existing = db.execute(
            "SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?",
            (post_id, user_id),
        ).fetchone()
        if not existing:
            # Zaten beğenilmemiş - 404 yerine başarılı döndür (idempotent)
            return MessageResponse(success=True, message="Beğeni zaten yoktu")

        db.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?", (post_id, user_id))
        db.execute(
            "UPDATE posts SET likes_count = MAX(0, likes_count - 1) WHERE post_id = ?",
            (post_id,),
        )
        db.commit()

        return MessageResponse(success=True, message="Beğeni kaldırıldı")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beğeni kaldırılırken hata: {e}")


# ══════════════════════════════════════════════════════════════
# COMMENTS
# ══════════════════════════════════════════════════════════════

@router.post("/posts/{post_id}/comments", status_code=201)
def add_comment(post_id: str, req: CommentRequest, db: sqlite3.Connection = Depends(get_db)):
    """Post'a yorum ekler."""
    try:
        post = db.execute("SELECT user_id FROM posts WHERE post_id = ?", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Post bulunamadı")

        comment_id = f"cmt-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()

        # comments tablosu yoksa oluştur
        db.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id TEXT PRIMARY KEY,
                post_id    TEXT NOT NULL,
                user_id    TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at TEXT NOT NULL,
                parent_id  TEXT DEFAULT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(post_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        # Mevcut tabloya parent_id ekle (hata verirse zaten var demektir)
        try:
            db.execute("ALTER TABLE comments ADD COLUMN parent_id TEXT DEFAULT NULL")
        except Exception:
            pass

        db.execute(
            "INSERT INTO comments (comment_id, post_id, user_id, content, created_at, parent_id) VALUES (?,?,?,?,?,?)",
            (comment_id, post_id, req.user_id, req.content, now, req.parent_id),
        )
        try:
            db.execute(
                "UPDATE posts SET comments_count = comments_count + 1 WHERE post_id = ?",
                (post_id,),
            )
        except Exception:
            pass  # comments_count sutunu yoksa gec
            
        # Bildirim oluştur
        if post and post[0] != req.user_id:
            create_notification(
                db=db,
                user_id=post[0],
                actor_id=req.user_id,
                notif_type="comment",
                post_id=post_id,
                comment_id=comment_id
            )
            
        db.commit()

        return {"success": True, "data": {"comment_id": comment_id}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum eklenirken hata: {e}")


@router.get("/posts/{post_id}/comments")
def get_comments(post_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Post'un yorumlarını listeler."""
    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id TEXT PRIMARY KEY,
                post_id    TEXT NOT NULL,
                user_id    TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at TEXT NOT NULL,
                parent_id  TEXT DEFAULT NULL
            )
        """)
        try:
            db.execute("ALTER TABLE comments ADD COLUMN parent_id TEXT DEFAULT NULL")
        except Exception:
            pass

        rows = db.execute(
            """SELECT c.comment_id, c.user_id, u.username, c.content, c.created_at, c.parent_id
               FROM comments c
               LEFT JOIN users u ON c.user_id = u.user_id
               WHERE c.post_id = ?
               ORDER BY c.created_at ASC""",
            (post_id,),
        ).fetchall()

        return [
            {
                "comment_id": r[0],
                "user_id": r[1],
                "username": r[2] or "Bilinmeyen",
                "content": r[3],
                "created_at": r[4],
                "parent_id": r[5],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorumlar alınırken hata: {e}")


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: str,
    user_id: str = Query(..., description="Yorumu silen kullanıcı ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """Kullanıcının kendi yorumunu siler."""
    try:
        comment = db.execute(
            "SELECT user_id, post_id FROM comments WHERE comment_id = ?", (comment_id,)
        ).fetchone()
        if not comment:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı.")
        if comment[0] != user_id:
            raise HTTPException(status_code=403, detail="Bu yorumu silme yetkiniz yok.")

        db.execute("DELETE FROM comments WHERE comment_id = ?", (comment_id,))
        try:
            db.execute(
                "UPDATE posts SET comments_count = MAX(0, comments_count - 1) WHERE post_id = ?",
                (comment[1],),
            )
        except Exception:
            pass
        db.commit()
        return MessageResponse(success=True, message="Yorum silindi.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum silinirken hata: {e}")


class ReportRequest(BaseModel):
    user_id: str
    reason: Optional[str] = "Uygunsuz içerik"


@router.post("/comments/{comment_id}/report", status_code=201)
def report_comment(comment_id: str, req: ReportRequest, db: sqlite3.Connection = Depends(get_db)):
    """Bir yorumu raporlar."""
    try:
        comment = db.execute(
            "SELECT comment_id FROM comments WHERE comment_id = ?", (comment_id,)
        ).fetchone()
        if not comment:
            raise HTTPException(status_code=404, detail="Yorum bulunamadı.")

        # Rapor tablosu yoksa oluştur
        db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_id TEXT NOT NULL,
                reporter_user_id TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (comment_id) REFERENCES comments(comment_id)
            )
        """)
        now = datetime.utcnow().isoformat()
        db.execute(
            "INSERT INTO reports (comment_id, reporter_user_id, reason, created_at) VALUES (?,?,?,?)",
            (comment_id, req.user_id, req.reason, now),
        )
        db.commit()
        return MessageResponse(success=True, message="Yorum başarıyla raporlandı.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Raporlama sırasında hata: {e}")
