from sqlalchemy.orm import Session
from app.models.social import Save, Post

class SaveService:
    def __init__(self, db: Session):
        self.db = db

    def save_post(self, user_id: str, post_id: str) -> bool:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError("Post bulunamadı")

        existing = self.db.query(Save).filter(Save.user_id == user_id, Save.post_id == post_id).first()
        if existing:
            return False

        save_entry = Save(user_id=user_id, post_id=post_id)
        self.db.add(save_entry)
        self.db.commit()
        return True

    def unsave_post(self, user_id: str, post_id: str) -> bool:
        existing = self.db.query(Save).filter(Save.user_id == user_id, Save.post_id == post_id).first()
        if not existing:
            return False

        self.db.delete(existing)
        self.db.commit()
        return True

    def get_saved_posts(self, user_id: str):
        saves = self.db.query(Save).filter(Save.user_id == user_id).all()
        saved_posts = []
        for s in saves:
            if s.post:
                saved_posts.append(s.post)
        return saved_posts