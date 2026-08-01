import logging

from sqlalchemy.orm import Session

from app.models.social import Profile
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_profile(self, user_id: str) -> Profile | None:
        return self.user_repo.get_user_by_id(user_id)

    def update_profile(
        self, 
        user_id: str, 
        username: str | None = None, 
        display_name: str | None = None, 
        bio: str | None = None, 
        avatar_url: str | None = None
    ) -> Profile:
        
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("Kullanıcı bulunamadı.")
            
        # Optional: Add username uniqueness validation logic here
            
        if username is not None:
            user.username = username
        if display_name is not None:
            user.display_name = display_name
        if bio is not None:
            user.bio = bio
        if avatar_url is not None:
            user.avatar_url = avatar_url
            
        self.db.commit()
        self.db.refresh(user)
        return user
