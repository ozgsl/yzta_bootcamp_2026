from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.domain.schemas import (
    MessageResponse,
    OutfitItemResponse,
    PostCreate,
    PostResponse,
)
from app.models.outfit import Outfit, OutfitItem
from app.models.social import Follow, Like, Post, Profile, Save
from app.models.wardrobe import WardrobeItem


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, post: PostCreate) -> MessageResponse:
        profile = self.db.scalars(select(Profile).where(Profile.id == post.user_id)).first()
        if not profile:
            raise HTTPException(status_code=404, detail='Kullanıcı bulunamadı')

        new_post = Post(
            user_id=post.user_id,
            image_url=post.image_url,
            content=post.caption,
            visibility=post.visibility,
            ai_training_consent=post.ai_training_consent
        )
        self.db.add(new_post)
        self.db.commit()
        self.db.refresh(new_post)

        if post.outfit_items:
            # Conceptually, post outfit items could be saved in an Outfit structure linked to this post.
            # Assuming outfit_id is used or we create a new outfit for the post.
            outfit = Outfit(
                user_id=post.user_id,
                description=f"Post {new_post.id} Outfit",
                context_json='{"etkinlik": "Post"}'
            )
            self.db.add(outfit)
            self.db.commit()
            
            for item_id in post.outfit_items:
                oi = OutfitItem(outfit_id=outfit.id, item_id=item_id)
                self.db.add(oi)
            self.db.commit()
            
            new_post.outfit_id = str(outfit.id)
            self.db.commit()

        return MessageResponse(success=True, message='Post başarıyla oluşturuldu', data={"post_id": str(new_post.id)})

    def _build_post_response(self, post: Post, profile: Profile, viewer_id: str | None = None) -> PostResponse:
        is_liked = False
        is_saved = False
        if viewer_id:
            is_liked = self.db.scalars(select(1).where(Like.post_id == post.id, Like.user_id == viewer_id)).first() is not None
            is_saved = self.db.scalars(select(1).where(Save.post_id == post.id, Save.user_id == viewer_id)).first() is not None

        outfit_items = []
        if post.outfit_id:
            outfit = self.db.scalars(select(Outfit).where(Outfit.id == post.outfit_id)).first()
            if outfit:
                for oi in outfit.items:
                    # In a real app, you might want to fetch WardrobeItem image
                    wi = self.db.scalars(select(WardrobeItem).where(WardrobeItem.id == oi.item_id)).first()
                    img_url = wi.storage_path if wi else None
                    cat = wi.subcategory.name if wi and wi.subcategory else "diğer"
                    outfit_items.append(OutfitItemResponse(item_id=str(oi.item_id), category=cat, image_url=img_url))

        # We assume active_title is handled via bio or a new column, using None for now as it's optional
        return PostResponse(
            post_id=str(post.id),
            user_id=str(profile.id),
            username=profile.username or "",
            display_name=profile.display_name or "",
            avatar_url=profile.avatar_url,
            active_title=None,
            image_url=post.image_url,
            caption=post.content or "",
            visibility=post.visibility,
            ai_training_consent=post.ai_training_consent,
            likes_count=post.likes_count,
            comments_count=len(post.comments), # In production, use count query if big
            is_liked=is_liked,
            is_saved=is_saved,
            outfit_items=outfit_items,
            created_at=post.created_at.isoformat() if post.created_at else "",
        )

    def get_user_posts(self, user_id: str, viewer_id: str | None = None) -> list[PostResponse]:
        query = select(Post, Profile).join(Profile, Post.user_id == Profile.id).where(Post.user_id == user_id)
        
        if viewer_id and viewer_id != user_id:
            # Check follows
            is_following = self.db.scalars(
                select(1).where(Follow.follower_id == viewer_id, Follow.following_id == user_id)
            ).first() is not None
            
            if is_following:
                query = query.where(Post.visibility.in_(['public', 'followers']))
            else:
                query = query.where(Post.visibility == 'public')
        elif not viewer_id:
            query = query.where(Post.visibility == 'public')

        query = query.order_by(Post.created_at.desc())
        results = self.db.execute(query).all()
        
        return [self._build_post_response(post, profile, viewer_id) for post, profile in results]

    def get_feed(self, user_id: str, limit: int = 20) -> list[PostResponse]:
        # public posts + followers posts + own posts
        
        # Subquery for following
        following_subquery = select(Follow.following_id).where(Follow.follower_id == user_id)
        
        query = select(Post, Profile).join(Profile, Post.user_id == Profile.id).where(
            or_(
                Post.user_id == user_id,
                Post.visibility == 'public',
                and_(Post.visibility == 'followers', Post.user_id.in_(following_subquery))
            )
        ).order_by(Post.created_at.desc()).limit(limit)
        
        return [self._build_post_response(post, profile, user_id) for post, profile in results]

    def get_post_by_id(self, post_id: str) -> Post | None:
        return self.db.scalars(select(Post).where(Post.id == post_id)).first()

    def delete_post(self, post_id: str, user_id: str) -> MessageResponse:
        post = self.db.scalars(select(Post).where(Post.id == post_id)).first()
        if not post:
            raise HTTPException(status_code=404, detail="Gönderi bulunamadı")
        if str(post.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Bu gönderiyi silme yetkiniz yok")

        # Outfit silinmeli mi? CASCADE ondelete varsa OutfitItem'lar uçar
        # Fakat biz Post'u siliyoruz, eğer Outfit de Post'a aitse silebiliriz, ancak relationship tanımlamadık.
        if post.outfit_id:
            outfit = self.db.scalars(select(Outfit).where(Outfit.id == post.outfit_id)).first()
            if outfit:
                self.db.delete(outfit)

        self.db.delete(post)
        self.db.commit()
        return MessageResponse(success=True, message="Gönderi silindi")

    def update_post(self, post_id: str, user_id: str, caption: str | None) -> MessageResponse:
        post = self.db.scalars(select(Post).where(Post.id == post_id)).first()
        if not post:
            raise HTTPException(status_code=404, detail="Gönderi bulunamadı")
        if str(post.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Bu gönderiyi düzenleme yetkiniz yok")

        if caption is not None:
            post.content = caption
            self.db.commit()
            
        return MessageResponse(success=True, message="Gönderi güncellendi")

    def get_saved_posts(self, user_id: str) -> list[PostResponse]:
        query = select(Post, Profile).join(Profile, Post.user_id == Profile.id).join(Save, Post.id == Save.post_id).where(Save.user_id == user_id).order_by(Save.created_at.desc())
        results = self.db.execute(query).all()
        return [self._build_post_response(post, profile, user_id) for post, profile in results]

    def save_post(self, post_id: str, user_id: str) -> MessageResponse:
        existing_save = self.db.scalars(select(Save).where(Save.post_id == post_id, Save.user_id == user_id)).first()
        if not existing_save:
            new_save = Save(post_id=post_id, user_id=user_id)
            self.db.add(new_save)
            self.db.commit()
        return MessageResponse(success=True, message="Kaydedildi")

    def unsave_post(self, post_id: str, user_id: str) -> MessageResponse:
        save = self.db.scalars(select(Save).where(Save.post_id == post_id, Save.user_id == user_id)).first()
        if save:
            self.db.delete(save)
            self.db.commit()
        return MessageResponse(success=True, message="Kayıtlardan kaldırıldı")
