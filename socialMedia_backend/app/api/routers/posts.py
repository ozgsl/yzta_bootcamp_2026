from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.domain.schemas import PostCreate, PostResponse
from app.models.base import get_db
from app.services.post_service import PostService
from app.services.save_service import SaveService

router = APIRouter()

def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)

def get_save_service(db: Session = Depends(get_db)) -> SaveService:
    return SaveService(db)

@router.post("/", status_code=201)
def create_post(
    request: PostCreate, 
    service: PostService = Depends(get_post_service)
):
    try:
        new_post = service.create_post(
            user_id=request.user_id,
            image_url=request.image_url,
            caption=request.caption,
            visibility=request.visibility,
            outfit_id=request.outfit_id,
            ai_training_consent=request.ai_training_consent
        )
        return {"mesaj": "Post created successfully", "id": str(new_post.id)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{post_id}")
def delete_post(
    post_id: str, 
    user_id: str, 
    service: PostService = Depends(get_post_service)
):
    try:
        service.delete_post(post_id, user_id)
        return {"mesaj": "Post deleted successfully", "id": post_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{post_id}/save")
def save_post(post_id: str, user_id: str, service: SaveService = Depends(get_save_service)):
    try:
        success = service.save_post(user_id, post_id)
        if not success:
            raise HTTPException(status_code=409, detail="Post already saved")
        return {"success": True, "message": "Post saved"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{post_id}/save")
def unsave_post(post_id: str, user_id: str, service: SaveService = Depends(get_save_service)):
    try:
        success = service.unsave_post(user_id, post_id)
        if not success:
            return {"success": True, "message": "Post was not saved"}
        return {"success": True, "message": "Post unsaved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/saved_posts", response_model=List[PostResponse])
def get_saved_posts(user_id: str, service: SaveService = Depends(get_save_service)):
    try:
        posts = service.get_saved_posts(user_id)
        return [{
            "post_id": str(p.id),
            "user_id": str(p.user_id),
            "username": p.user.username if p.user else "",
            "display_name": p.user.display_name if p.user else "",
            "avatar_url": p.user.avatar_url if p.user else None,
            "image_url": p.image_url or "",
            "caption": p.content,
            "visibility": p.visibility,
            "likes_count": p.likes_count,
            "comments_count": len(p.comments),
            "created_at": p.created_at.isoformat() if p.created_at else ""
        } for p in posts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
