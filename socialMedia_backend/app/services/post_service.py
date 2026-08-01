import logging

from sqlalchemy.orm import Session

from app.models.social import Post
from app.repositories.post_repository import PostRepository

logger = logging.getLogger(__name__)

class PostService:
    def __init__(self, db: Session):
        self.db = db
        self.post_repo = PostRepository(db)

    def create_post(
        self, 
        user_id: str, 
        image_url: str, 
        caption: str | None = None, 
        visibility: str = "public", 
        outfit_id: str | None = None, 
        ai_training_consent: bool = False
    ) -> Post:
        
        # Validations could go here (e.g. check if image_url is valid, if visibility is in enum)
        if visibility not in ["public", "followers", "private"]:
            raise ValueError("Geçersiz görünürlük ayarı.")
            
        new_post = Post(
            user_id=user_id,
            image_url=image_url,
            caption=caption,
            visibility=visibility,
            outfit_id=outfit_id,
            ai_training_consent=ai_training_consent
        )
        self.db.add(new_post)
        self.db.commit()
        self.db.refresh(new_post)
        return new_post

    def get_post(self, post_id: str) -> Post | None:
        return self.post_repo.get_post_by_id(post_id)

    def delete_post(self, post_id: str, user_id: str):
        post = self.post_repo.get_post_by_id(post_id)
        if not post:
            raise ValueError("Post bulunamadı.")
            
        if str(post.user_id) != user_id:
            raise PermissionError("Bu postu silme yetkiniz yok.")
            
        self.db.delete(post)
        self.db.commit()

    def get_user_posts(self, target_user_id: str, viewer_id: str) -> list[Post]:
        """
        Applies visibility rules at the service level, though usually FeedService handles broader visibility.
        This is for viewing a specific user's profile.
        """
        # Logic to check follows if visibility is 'followers'
        # For simplicity, returning all from repo and letting FeedService or Router filter, 
        # but ideally the service filters it.
        # This will be handled by the SQL query originally in Feed/Profile.
