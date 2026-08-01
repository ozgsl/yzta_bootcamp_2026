from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.domain.schemas import CommentRequest, LikeRequest
from app.models.base import get_db
from app.services.comment_service import CommentService
from app.services.like_service import LikeService

router = APIRouter()

def get_like_service(db: Session = Depends(get_db)) -> LikeService:
    return LikeService(db)

def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    return CommentService(db)

@router.post("/")
def like_post(
    request: LikeRequest, 
    service: LikeService = Depends(get_like_service)
):
    try:
        success = service.like_post(user_id=request.user_id, post_id=request.post_id)
        if not success:
            raise HTTPException(status_code=409, detail="Bu postu zaten beğendiniz")
        return {"success": True, "message": "Post beğenildi"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/")
def unlike_post(
    request: LikeRequest, 
    service: LikeService = Depends(get_like_service)
):
    try:
        success = service.unlike_post(user_id=request.user_id, post_id=request.post_id)
        if not success:
            return {"success": True, "message": "Beğeni zaten yoktu"}
        return {"success": True, "message": "Beğeni kaldırıldı"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/comments")
def add_comment(
    request: CommentRequest, 
    service: CommentService = Depends(get_comment_service)
):
    try:
        comment = service.add_comment(
            post_id=request.post_id,
            user_id=request.user_id,
            content=request.content,
            parent_id=request.parent_id
        )
        return {"success": True, "message": "Yorum eklendi", "id": str(comment.id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comments/{post_id}")
def get_comments(
    post_id: str, 
    service: CommentService = Depends(get_comment_service)
):
    try:
        return service.get_post_comments(post_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: str, 
    user_id: str, 
    service: CommentService = Depends(get_comment_service)
):
    try:
        service.delete_comment(comment_id, user_id)
        return {"success": True, "message": "Yorum silindi"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
