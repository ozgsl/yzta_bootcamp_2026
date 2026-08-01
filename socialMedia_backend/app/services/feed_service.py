import logging

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.social import Follow, Post

logger = logging.getLogger(__name__)

class FeedService:
    """
    Handles fetching and ranking posts for different feeds.
    Includes N+1 Query Optimizations.
    """
    def __init__(self, db: Session):
        self.db = db

    def _get_base_query(self):
        """
        Base query with eager loading to prevent N+1 issues.
        We use joinedload for User (Many-to-One) and selectinload for Comments/Likes (One-to-Many).
        """
        return select(Post).options(
            joinedload(Post.user).load_only("id", "username", "avatar_url", "display_name", "profile_visibility"),
            selectinload(Post.comments),
            selectinload(Post.likes)
        ).where(Post.deleted_at == None)

    def get_timeline(self, viewer_id: str, limit: int = 20, cursor: str = None) -> list[Post]:
        """Following feed with cursor pagination."""
        following_ids_query = select(Follow.following_id).where(Follow.follower_id == viewer_id)
        
        q = self._get_base_query().where(Post.user_id.in_(following_ids_query))
        
        if cursor:
            # Simple cursor implementation assuming cursor is an ISO datetime string of created_at
            q = q.where(Post.created_at < cursor)
            
        return self.db.scalars(q.order_by(desc(Post.created_at)).limit(limit)).all()

    def get_discover_feed(self, viewer_id: str, limit: int = 20, cursor: str = None) -> list[Post]:
        """Public posts discovery with cursor pagination."""
        following_ids_query = select(Follow.following_id).where(Follow.follower_id == viewer_id)
        
        q = self._get_base_query().where(
            Post.visibility == 'public',
            Post.user_id.not_in(following_ids_query),
            Post.user_id != viewer_id
        )
        
        if cursor:
            q = q.where(Post.created_at < cursor)
            
        return self.db.scalars(q.order_by(desc(Post.created_at)).limit(limit)).all()

    def get_trending_feed(self, limit: int = 20, cursor: str = None) -> list[Post]:
        """Trending posts based on likes count."""
        q = self._get_base_query().where(Post.visibility == 'public')
        
        if cursor:
            # Assuming cursor for trending is likes_count_cursor, created_at_cursor composite string
            # Simplified for now to just created_at
            q = q.where(Post.created_at < cursor)
            
        return self.db.scalars(q.order_by(desc(Post.likes_count), desc(Post.created_at)).limit(limit)).all()

    def get_profile_posts(self, profile_owner_id: str, viewer_id: str, limit: int = 20, cursor: str = None) -> list[Post]:
        """Profile posts respecting visibility."""
        is_self = str(profile_owner_id) == str(viewer_id)
        is_following = False
        if not is_self:
            is_following = self.db.scalars(
                select(Follow).where(Follow.follower_id == viewer_id, Follow.following_id == profile_owner_id)
            ).first() is not None

        q = self._get_base_query().where(Post.user_id == profile_owner_id)
        
        if cursor:
            q = q.where(Post.created_at < cursor)

        if is_self:
            # Can see everything
            pass
        elif is_following:
            q = q.where(Post.visibility.in_(['public', 'followers']))
        else:
            q = q.where(Post.visibility == 'public')

        return self.db.scalars(q.order_by(desc(Post.created_at)).limit(limit)).all()
