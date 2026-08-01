
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, load_only

from app.models.social import Profile


class SearchService:
    def __init__(self, db: Session):
        self.db = db

    def search_users(self, query: str, viewer_id: str, limit: int = 20) -> list[Profile]:
        """
        Searches users by username or display name, applying privacy filters.
        """
        q = select(Profile).where(
            or_(
                Profile.username.ilike(f"%{query}%"),
                Profile.display_name.ilike(f"%{query}%")
            )
        ).options(
            load_only("id", "username", "display_name", "avatar_url", "profile_visibility", "followers_count")
        )
        
        users = self.db.scalars(q.limit(limit)).all()
        
        # In memory filtering for complex logic or just return directly depending on business logic
        # Assuming viewers can't see profiles that blocked them (blocked logic not implemented yet)
        return [user for user in users if self._can_view(viewer_id, user)]

    def _can_view(self, viewer_id: str, user: Profile) -> bool:
        if str(user.id) == viewer_id:
            return True
        # In the future, check if user blocked viewer_id
        return True
