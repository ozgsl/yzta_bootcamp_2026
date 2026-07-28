
import sqlite3
import uuid
from fastapi import HTTPException
from app.domain.schemas import PostCreate, PostResponse, OutfitItemResponse, CommentResponse, MessageResponse

class PostRepository:
    @staticmethod
    def create_post(db: sqlite3.Connection, post: PostCreate) -> MessageResponse:
        post_id = str(uuid.uuid4())
        user = db.execute('SELECT user_id FROM users WHERE user_id = ?', (post.user_id,)).fetchone()
        if not user: raise HTTPException(status_code=404, detail='Kullanıcı bulunamadı')
        
        db.execute(
            'INSERT INTO posts (post_id, user_id, image_url, caption, visibility, ai_training_consent) VALUES (?, ?, ?, ?, ?, ?)',
            (post_id, post.user_id, post.image_url, post.caption, post.visibility, int(post.ai_training_consent))
        )
        
        if post.outfit_items:
            for item_id in post.outfit_items:
                db.execute(
                    'INSERT INTO post_outfit_items (post_id, item_id, category, image_url) VALUES (?, ?, ?, ?)',
                    (post_id, item_id, 'diğer', None)
                )
        db.commit()
        return MessageResponse(success=True, message='Post başarıyla oluşturuldu', data={"post_id": post_id})

    @staticmethod
    def _build_post_response(db, row, viewer_id=None):
        """Tek bir post satırını PostResponse'a çevirir."""
        is_liked = False
        is_saved = False
        if viewer_id:
            is_liked = db.execute('SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?', (row['post_id'], viewer_id)).fetchone() is not None
            try:
                is_saved = db.execute('SELECT 1 FROM saved_posts WHERE post_id = ? AND user_id = ?', (row['post_id'], viewer_id)).fetchone() is not None
            except Exception:
                is_saved = False
        outfit_rows = db.execute('''
            SELECT poi.item_id, poi.category, k.foto_url as image_url
            FROM post_outfit_items poi
            LEFT JOIN kiyafetler k ON CAST(poi.item_id AS INTEGER) = k.id
            WHERE poi.post_id = ?
        ''', (row['post_id'],)).fetchall()
        outfit_items = [OutfitItemResponse(item_id=oi['item_id'], category=oi['category'], image_url=oi['image_url']) for oi in outfit_rows]
        return PostResponse(
            post_id=row['post_id'], user_id=row['user_id'],
            username=row['username'], display_name=row['display_name'],
            avatar_url=row['avatar_url'],
            active_title=row['active_title'] if 'active_title' in row.keys() else None,
            image_url=row['image_url'], caption=row['caption'],
            visibility=row['visibility'],
            ai_training_consent=bool(row['ai_training_consent']),
            likes_count=row['likes_count'],
            comments_count=dict(row).get('comments_count', 0),
            is_liked=is_liked, is_saved=is_saved,
            outfit_items=outfit_items, created_at=row['created_at']
        )

    @staticmethod
    def get_user_posts(db: sqlite3.Connection, user_id: str, viewer_id: str = None):
        base_select = 'SELECT p.*, u.username, u.display_name, u.avatar_url, u.active_title FROM posts p JOIN users u ON p.user_id = u.user_id'
        if viewer_id and viewer_id == user_id:
            rows = db.execute(
                f"{base_select} WHERE p.user_id = ? ORDER BY p.created_at DESC",
                (user_id,)
            ).fetchall()
        elif viewer_id:
            rows = db.execute(
                f"{base_select} WHERE p.user_id = ? AND (p.visibility = 'public' OR (p.visibility = 'followers' AND EXISTS (SELECT 1 FROM follows WHERE follower_id = ? AND following_id = p.user_id))) ORDER BY p.created_at DESC", (user_id, viewer_id)
            ).fetchall()
        else:
            rows = db.execute(
                f"{base_select} WHERE p.user_id = ? AND p.visibility = 'public' ORDER BY p.created_at DESC",
                (user_id,)
            ).fetchall()

        return [PostRepository._build_post_response(db, row, viewer_id) for row in rows]

    @staticmethod
    def get_feed(db: sqlite3.Connection, user_id: str, limit: int = 20):
        rows = db.execute(
            "SELECT p.*, u.username, u.display_name, u.avatar_url, u.active_title FROM posts p JOIN users u ON p.user_id = u.user_id WHERE (p.user_id = ? OR p.visibility = 'public' OR (p.visibility = 'followers' AND EXISTS (SELECT 1 FROM follows WHERE follower_id = ? AND following_id = p.user_id))) ORDER BY p.created_at DESC LIMIT ?", (user_id, user_id, limit)
        ).fetchall()
        return [PostRepository._build_post_response(db, row, user_id) for row in rows]
