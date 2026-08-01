from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.domain.schemas import (
    AnalyzeClothRequest,
    ClothAddRequest,
    ClothUpdateRequest,
    OutfitRecommendRequest, LaundryStatusRequest, FavoriteStatusRequest, ChatRequest,
)
from app.models.base import get_db
from app.services.outfit_service import OutfitService
from app.services.wardrobe_service import WardrobeService

router = APIRouter()

def get_wardrobe_service(db: Session = Depends(get_db)) -> WardrobeService:
    return WardrobeService(db)

def get_outfit_service(db: Session = Depends(get_db)) -> OutfitService:
    return OutfitService(db)

@router.post("/items")
def add_cloth(request: ClothAddRequest, w_service: WardrobeService = Depends(get_wardrobe_service)):
    try:
        # Pass filename to service to do AI classification and DB insert
        item = w_service.process_and_add_item(user_id=request.user_id, filename=request.image_url)
        return {"mesaj": "Clothing item added successfully", "message": "Clothing item added successfully", "id": str(item.id)}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/items/{item_id}/laundry")
def set_laundry_status(item_id: str, request: LaundryStatusRequest, w_service: WardrobeService = Depends(get_wardrobe_service)):
    """Quickly toggle laundry (dirty/clean) status of a clothing item."""
    try:
        w_service.set_laundry_status(item_id, request.user_id, request.is_in_laundry)
        return {"message": "Laundry status updated", "id": item_id, "is_dirty": request.is_in_laundry}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/items/{item_id}/favorite")
def set_favorite_status(item_id: str, request: FavoriteStatusRequest, w_service: WardrobeService = Depends(get_wardrobe_service)):
    """Quickly toggle favorite status of a clothing item."""
    try:
        w_service.set_favorite_status(item_id, request.user_id, request.is_favorite)
        return {"message": "Favorite status updated", "id": item_id, "is_favorite": request.is_favorite}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/chat")
def chat(request: ChatRequest, w_service: WardrobeService = Depends(get_wardrobe_service)):
    """Handles AI Stylist chat messages."""
    try:
        result = w_service.chat_with_stylist(request.user_id, request.message, request.message)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

@router.post("/analyze-image")
def analyze_cloth_image(request: AnalyzeClothRequest, w_service: WardrobeService = Depends(get_wardrobe_service)):
    """Analyzes clothing image using AI Provider."""
    if not request.gorsel_url:
        raise HTTPException(status_code=400, detail="gorsel_url is required.")
        
    try:
        result = w_service.analyze_image(request.gorsel_url)
        if not result.get("success"):
            raise HTTPException(status_code=503, detail=f"AI model hatası: {result.get('error', 'Bilinmeyen hata')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis error: {e!s}")

@router.get("/items/{user_id}")
def get_clothes(user_id: str, w_service: WardrobeService = Depends(get_wardrobe_service)):
    return w_service.get_user_items(user_id)

@router.put("/items/{item_id}")
def update_cloth(item_id: str, request: ClothUpdateRequest, w_service: WardrobeService = Depends(get_wardrobe_service)):
    try:
        w_service.update_item(item_id, request.user_id, request.model_dump(exclude_unset=True))
        return {"mesaj": "Clothing item updated", "message": "Clothing item updated", "id": item_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/items/{item_id}")
def delete_cloth(item_id: str, user_id: str, w_service: WardrobeService = Depends(get_wardrobe_service)):
    try:
        w_service.delete_item(item_id, user_id)
        return {"mesaj": "Clothing item deleted", "message": "Clothing item deleted", "id": item_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/outfit/suggest")
def recommend_outfit(request: OutfitRecommendRequest, o_service: OutfitService = Depends(get_outfit_service)):
    try:
        # Mocking the AI call since we refactored AI logic to service placeholder
        outfit = o_service.generate_random_outfit(request.user_id)
        if not outfit:
            raise HTTPException(status_code=400, detail="No clothes available.")
        return {"id": str(outfit.id), "message": "Outfit recommended"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
