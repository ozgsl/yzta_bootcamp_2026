from __future__ import annotations
import uuid
from datetime import datetime
import sqlite3
from typing import Optional, List
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, Query

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


@router.post("/{post_id}/share", response_model=MessageResponse)
def share_post(
    post_id: str,
    user_id: str = Query(..., description="Paylaşan kullanıcı ID"),
    db: sqlite3.Connection = Depends(get_db),
):
    """Bir gönderiyi paylaşır (repost/share)."""
    try:
        # Post var mı kontrol et
        post = db.execute("SELECT post_id, user_id FROM posts WHERE post_id = ?", (post_id,)).fetchone()
        if not post:
            raise HTTPException(status_code=404, detail="Gönderi bulunamadı")
        
        # Share kaydı oluştur (basit bir shares tablosu)
        db.execute("""
            CREATE TABLE IF NOT EXISTS shares (
                share_id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        share_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        db.execute(
            "INSERT INTO shares (share_id, post_id, user_id, created_at) VALUES (?, ?, ?, ?)",
            (share_id, post_id, user_id, now)
        )
        
        # Post shares_count artır (varsa)
        try:
            db.execute("UPDATE posts SET shares_count = shares_count + 1 WHERE post_id = ?", (post_id,))
        except Exception:
            pass  # shares_count sütunu yoksa geç
        
        # Bildirim oluştur (kendi postunu paylaşmıyorsa)
        if post[1] != user_id:
            create_notification(
                db=db,
                user_id=post[1],
                actor_id=user_id,
                notif_type="share",
                post_id=post_id
            )
        
        db.commit()
        return MessageResponse(success=True, message="Gönderi paylaşıldı", data={"share_id": share_id})
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=f"Paylaşım hatası: {e}")

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


@router.post('/{post_id}/save', response_model=MessageResponse)
def save_post(post_id: str, req: LikeRequest, db: sqlite3.Connection = Depends(get_db)):
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
            (req.user_id, post_id, saved_at),
        )
        
        post = db.execute("SELECT user_id FROM posts WHERE post_id = ?", (post_id,)).fetchone()
        if post and post["user_id"] != req.user_id:
            create_notification(
                db=db,
                user_id=post["user_id"],
                actor_id=req.user_id,
                notif_type="save",
                post_id=post_id
            )
        
        db.commit()
        return MessageResponse(success=True, message="Kaydedildi")
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


# ═══════════════════════════════════════════════════════════════════════════════
# LIKES
# ═══════════════════════════════════════════════════════════════════════════════

class LikeRequest(BaseModel):
    user_id: str


@router.post("/{post_id}/like", response_model=MessageResponse)
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


@router.delete("/{post_id}/like", response_model=MessageResponse)
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


# ═══════════════════════════════════════════════════════════════════════════════
# COMMENTS
# ═══════════════════════════════════════════════════════════════════════════════

class CommentRequest(BaseModel):
    user_id: str
    content: str
    parent_id: Optional[str] = None


@router.post("/{post_id}/comments", response_model=MessageResponse)
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
            pass  # comments_count sutunu yoksa geç
            
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

        return MessageResponse(success=True, message="Yorum eklendi", data={"comment_id": comment_id})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorum eklenirken hata: {e}")


@router.get("/{post_id}/comments")
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
                "comment_id": r["comment_id"],
                "user_id": r["user_id"],
                "username": r["username"],
                "content": r["content"],
                "created_at": r["created_at"],
                "parent_id": r["parent_id"],
            }
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yorumlar listelenirken hata: {e}")
