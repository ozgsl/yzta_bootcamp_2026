
import sqlite3
import uuid
from fastapi import HTTPException
from app.domain.schemas import PostCreate, PostResponse, OutfitItemResponse, CommentResponse, MessageResponse


def _ensure_active_title_column(db: sqlite3.Connection):
    """active_title kolonu yoksa ekler (eski veritabanı uyumluluğu)."""
    try:
        db.execute("SELECT active_title FROM users LIMIT 1")
    except sqlite3.OperationalError:
        try:
            db.execute("ALTER TABLE users ADD COLUMN active_title TEXT DEFAULT NULL")
            db.commit()
        except Exception:
            pass


class PostRepository:
    @staticmethod
    def create_post(db: sqlite3.Connection, post: PostCreate) -> MessageResponse:
        _ensure_active_title_column(db)
        post_id = str(uuid.uuid4())
        user = db.execute('SELECT user_id FROM users WHERE user_id = ?', (post.user_id,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail='Kullanıcı bulunamadı')

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
            is_liked = db.execute(
                'SELECT 1 FROM likes WHERE post_id = ? AND user_id = ?',
                (row['post_id'], viewer_id)
            ).fetchone() is not None
            try:
                is_saved = db.execute(
                    'SELECT 1 FROM saved_posts WHERE post_id = ? AND user_id = ?',
                    (row['post_id'], viewer_id)
                ).fetchone() is not None
            except Exception:
                is_saved = False

        outfit_rows = db.execute('''
            SELECT poi.item_id, poi.category, k.foto_url as image_url
            FROM post_outfit_items poi
            LEFT JOIN kiyafetler k ON CAST(poi.item_id AS INTEGER) = k.id
            WHERE poi.post_id = ?
        ''', (row['post_id'],)).fetchall()
        outfit_items = [
            OutfitItemResponse(item_id=oi['item_id'], category=oi['category'], image_url=oi['image_url'])
            for oi in outfit_rows
        ]

        row_dict = dict(row)
        return PostResponse(
            post_id=row_dict['post_id'],
            user_id=row_dict['user_id'],
            username=row_dict['username'],
            display_name=row_dict['display_name'],
            avatar_url=row_dict['avatar_url'],
            active_title=row_dict.get('active_title'),
            image_url=row_dict['image_url'],
            caption=row_dict['caption'],
            visibility=row_dict['visibility'],
            ai_training_consent=bool(row_dict['ai_training_consent']),
            likes_count=row_dict['likes_count'],
            comments_count=row_dict.get('comments_count', 0),
            is_liked=is_liked,
            is_saved=is_saved,
            outfit_items=outfit_items,
            created_at=row_dict['created_at'],
        )

    @staticmethod
    def get_user_posts(db: sqlite3.Connection, user_id: str, viewer_id: str = None):
        _ensure_active_title_column(db)
        base_select = (
            'SELECT p.*, u.username, u.display_name, u.avatar_url, u.active_title '
            'FROM posts p JOIN users u ON p.user_id = u.user_id'
        )
        if viewer_id and viewer_id == user_id:
            rows = db.execute(
                f"{base_select} WHERE p.user_id = ? ORDER BY p.created_at DESC",
                (user_id,)
            ).fetchall()
        elif viewer_id:
            rows = db.execute(
                f"{base_select} WHERE p.user_id = ? AND (p.visibility = 'public' OR "
                f"(p.visibility = 'followers' AND EXISTS ("
                f"SELECT 1 FROM follows WHERE follower_id = ? AND following_id = p.user_id"
                f"))) ORDER BY p.created_at DESC",
                (user_id, viewer_id)
            ).fetchall()
        else:
            rows = db.execute(
                f"{base_select} WHERE p.user_id = ? AND p.visibility = 'public' ORDER BY p.created_at DESC",
                (user_id,)
            ).fetchall()

        return [PostRepository._build_post_response(db, row, viewer_id) for row in rows]

    @staticmethod
    def get_feed(db: sqlite3.Connection, user_id: str, limit: int = 20):
        _ensure_active_title_column(db)
        rows = db.execute(
            "SELECT p.*, u.username, u.display_name, u.avatar_url, u.active_title "
            "FROM posts p JOIN users u ON p.user_id = u.user_id "
            "WHERE (p.user_id = ? OR p.visibility = 'public' OR "
            "(p.visibility = 'followers' AND EXISTS ("
            "SELECT 1 FROM follows WHERE follower_id = ? AND following_id = p.user_id"
            "))) ORDER BY p.created_at DESC LIMIT ?",
            (user_id, user_id, limit)
        ).fetchall()
        return [PostRepository._build_post_response(db, row, user_id) for row in rows]
