from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter()

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)

@router.get("/wardrobe/{user_id}")
def get_wardrobe_stats(user_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_wardrobe_stats(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/engagement/{user_id}")
def get_engagement_stats(user_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return service.get_engagement_stats(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/achievements/{user_id}")
def get_achievements(user_id: str, service: AnalyticsService = Depends(get_analytics_service)):
    try:
        return {"achievements": service.get_achievements(user_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
