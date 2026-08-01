from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.domain.schemas import UserResponse, ProfileUpdateRequest
from app.models.base import get_db
from app.services.user_service import UserService

router = APIRouter()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.get("/{user_id}", response_model=UserResponse)
def get_profile(user_id: str, service: UserService = Depends(get_user_service)):
    profile = service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    return {
        "user_id": str(profile.id),
        "email": profile.email,
        "username": profile.username or "",
        "display_name": profile.display_name or "",
        "avatar_url": profile.avatar_url,
        "bio": profile.bio,
        "followers_count": profile.followers_count,
        "following_count": profile.following_count,
        "created_at": str(profile.created_at)
    }

@router.put("/{user_id}", response_model=UserResponse)
def update_profile(
    user_id: str, 
    request: ProfileUpdateRequest, 
    service: UserService = Depends(get_user_service)
):
    try:
        updated = service.update_profile(
            user_id=user_id,
            username=request.username,
            display_name=request.display_name,
            bio=request.bio,
            avatar_url=request.avatar_url
        )
        return {
            "user_id": str(updated.id),
            "email": updated.email,
            "username": updated.username or "",
            "display_name": updated.display_name or "",
            "avatar_url": updated.avatar_url,
            "bio": updated.bio,
            "followers_count": updated.followers_count,
            "following_count": updated.following_count,
            "created_at": str(updated.created_at)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
