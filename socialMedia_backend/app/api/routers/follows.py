from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.domain.schemas import FollowersCountResponse, FollowRequest
from app.models.base import get_db
from app.services.follow_service import FollowService

router = APIRouter()

def get_follow_service(db: Session = Depends(get_db)) -> FollowService:
    return FollowService(db)

@router.post("/", response_model=FollowersCountResponse)
def follow_user(
    request: FollowRequest, 
    service: FollowService = Depends(get_follow_service)
):
    try:
        success = service.follow_user(follower_id=request.follower_id, following_id=request.following_id)
        if not success:
            raise HTTPException(status_code=409, detail="Bu kullanıcıyı zaten takip ediyorsunuz")
            
        return FollowersCountResponse(
            success=True, 
            message="Kullanıcı takip edildi",
            followers_count=service.get_followers_count(request.following_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/", response_model=FollowersCountResponse)
def unfollow_user(
    request: FollowRequest, 
    service: FollowService = Depends(get_follow_service)
):
    try:
        success = service.unfollow_user(follower_id=request.follower_id, following_id=request.following_id)
        if not success:
            return FollowersCountResponse(
                success=True, 
                message="Zaten takip edilmiyordu",
                followers_count=service.get_followers_count(request.following_id)
            )
            
        return FollowersCountResponse(
            success=True, 
            message="Takipten çıkıldı",
            followers_count=service.get_followers_count(request.following_id)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
