from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.domain.schemas import UserResponse
from app.models.social import Profile


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: str) -> Profile | None:
        try:
            return self.db.scalars(select(Profile).where(Profile.id == user_id)).first()
        except Exception:
            self.db.rollback()
            return None

    def get_user_profile(self, user_id: str) -> UserResponse:
        profile = self.get_user_by_id(user_id)

        if not profile:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
        
        return UserResponse(
            user_id=str(profile.id),
            email="", # Usually handled by Supabase Auth
            username=profile.username or "",
            display_name=profile.display_name or "",
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            followers_count=profile.followers_count,
            following_count=profile.following_count,
            created_at=profile.created_at.isoformat() if profile.created_at else "",
            profile_visibility=profile.profile_visibility,
            height=profile.height,
            weight=profile.weight,
            chest=profile.chest,
            waist=profile.waist,
            hips=profile.hips,
            location=profile.location,
            timezone=profile.timezone
        )

    def update_user_profile(
        self, user_id: str, 
        display_name: str | None = None, 
        bio: str | None = None, 
        avatar_url: str | None = None,
        height: str | None = None,
        weight: str | None = None,
        chest: str | None = None,
        waist: str | None = None,
        hips: str | None = None,
        location: str | None = None,
        timezone: str | None = None
    ) -> None:
        updates = {}
        fields = {
            "display_name": display_name,
            "bio": bio,
            "avatar_url": avatar_url,
            "height": height,
            "weight": weight,
            "chest": chest,
            "waist": waist,
            "hips": hips,
            "location": location,
            "timezone": timezone
        }
        
        for k, v in fields.items():
            if v is not None:
                updates[k] = v
            
        if not updates:
            return
            
        self.db.execute(
            update(Profile).where(Profile.id == user_id).values(**updates)
        )
        self.db.commit()

    def update_privacy_settings(self, user_id: str, profile_visibility: str) -> None:
        self.db.execute(
            update(Profile).where(Profile.id == user_id).values(profile_visibility=profile_visibility)
        )
        self.db.commit()

    def delete_account(self, user_id: str) -> None:
        profile = self.db.scalars(select(Profile).where(Profile.id == user_id)).first()
        if profile:
            self.db.delete(profile)
            self.db.commit()
