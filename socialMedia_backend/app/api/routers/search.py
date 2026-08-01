from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.services.search_service import SearchService

router = APIRouter()

def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    return SearchService(db)

@router.get("/users")
def search_users(
    q: str = Query(..., min_length=1),
    viewer_id: str = None,
    service: SearchService = Depends(get_search_service)
):
    try:
        users = service.search_users(query=q, viewer_id=viewer_id, limit=20)
        return {
            "query": q,
            "results": [
                {
                    "id": str(user.id),
                    "username": user.username,
                    "display_name": user.display_name,
                    "avatar_url": user.avatar_url,
                    "profile_visibility": user.profile_visibility,
                    "followers_count": user.followers_count
                } for user in users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
