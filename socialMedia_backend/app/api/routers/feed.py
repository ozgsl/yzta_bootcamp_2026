
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.services.feed_service import FeedService
from app.domain.schemas import FeedResponse, PostResponse

# Note: In a real app we'd use a Pydantic model for Response to serialize correctly

router = APIRouter()

def get_feed_service(db: Session = Depends(get_db)) -> FeedService:
    return FeedService(db)

@router.get("/", response_model=FeedResponse)
def get_timeline(
    viewer_id: str, 
    limit: int = Query(20, le=50), 
    cursor: str | None = None, 
    service: FeedService = Depends(get_feed_service)
):
    """
    Following tab equivalent using cursor pagination.
    """
    posts = service.get_timeline(viewer_id, limit, cursor)
    return {"posts": [{
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
    } for p in posts], "next_cursor": posts[-1].created_at.isoformat() if posts else None}

@router.get("/discover", response_model=FeedResponse)
def get_discover(
    viewer_id: str, 
    limit: int = Query(20, le=50), 
    cursor: str | None = None, 
    service: FeedService = Depends(get_feed_service)
):
    """
    Discover tab equivalent using cursor pagination.
    """
    posts = service.get_discover_feed(viewer_id, limit, cursor)
    return {"posts": [{
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
    } for p in posts], "next_cursor": posts[-1].created_at.isoformat() if posts else None}

@router.get("/trending", response_model=FeedResponse)
def get_trending(
    limit: int = Query(20, le=50), 
    cursor: str | None = None, 
    service: FeedService = Depends(get_feed_service)
):
    """
    Trending tab equivalent using cursor pagination.
    """
    posts = service.get_trending_feed(limit, cursor)
    return {"posts": [{
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
    } for p in posts], "next_cursor": posts[-1].created_at.isoformat() if posts else None}

@router.get("/profile/{profile_owner_id}", response_model=FeedResponse)
def get_profile_posts(
    profile_owner_id: str,
    viewer_id: str,
    limit: int = Query(20, le=50),
    cursor: str | None = None,
    service: FeedService = Depends(get_feed_service)
):
    """
    Profile page posts logic using cursor pagination.
    """
    posts = service.get_profile_posts(profile_owner_id, viewer_id, limit, cursor)
    return {"posts": [{
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
    } for p in posts], "next_cursor": posts[-1].created_at.isoformat() if posts else None}
