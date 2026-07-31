from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from pydantic import BaseModel
from typing import Optional, List
import json
from pathlib import Path

from app.core.database import get_db
from app.repositories.item_repository import ItemRepository
from app.services import ollama_client
from app.services.fashion_classifier import classifier as fashion_classifier

router = APIRouter(tags=["Wardrobe"])

# --- Models ---
class ClothCreateRequest(BaseModel):
    tur: str
    renk: str
    renk_hex: Optional[str] = None
    renk_kategori_id: Optional[str] = None
    marka: Optional[str] = None
    beden: Optional[str] = None
    kumas: Optional[str] = None
    kesim: Optional[str] = None
    yaka_tipi: Optional[str] = None
    kol_tipi: Optional[str] = None
    desen: Optional[str] = "düz"
    mevsim: Optional[str] = "tüm sezon"
    stil_etiketi: Optional[str] = None
    kullanim_sikligi: Optional[str] = None
    kombin_notu: Optional[str] = None
    temiz: bool = True
    foto_url: Optional[str] = None
    is_favorite: bool = False


class LaundryStatusRequest(BaseModel):
    is_dirty: bool


class FavoriteStatusRequest(BaseModel):
    is_favorite: bool


# Aliases for backwards compatibility
KiyafetEkleIstek = ClothCreateRequest


class ChatRequest(BaseModel):
    user_id: str
    mesaj: str
    hava_durumu: Optional[str] = None

ChatIstek = ChatRequest


class OutfitRecommendRequest(BaseModel):
    user_id: str
    etkinlik: str
    hava_durumu: str
    stil_tercihi: Optional[str] = ""

KombinOnerIstek = OutfitRecommendRequest


class ManualOutfitCreateRequest(BaseModel):
    user_id: str
    item_ids: List[int]
    aciklama: str


class AnalyzeClothRequest(BaseModel):
    gorsel_url: str

AnalyzeKiyafetIstek = AnalyzeClothRequest


# --- Endpoints ---
@router.post("/items")
def add_cloth(user_id: str, request: ClothCreateRequest, db: sqlite3.Connection = Depends(get_db)):
    """Adds a new cloth item to user's wardrobe."""
    repo = ItemRepository(db)
    data = request.model_dump()
    cloth_id = repo.add_cloth(user_id=user_id, **data)
    return {"id": cloth_id, "mesaj": "Clothing item added", "message": "Clothing item added"}


@router.get("/items/{user_id}")
def list_clothes(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Lists all clothes for a given user."""
    repo = ItemRepository(db)
    return repo.get_clothes(user_id)


@router.put("/items/{item_id}")
def update_cloth(item_id: int, request: ClothCreateRequest, db: sqlite3.Connection = Depends(get_db)):
    """Updates an existing cloth item."""
    repo = ItemRepository(db)
    data = request.model_dump()
    try:
        updated = repo.update_cloth(item_id=item_id, **data)
        if not updated:
            raise HTTPException(status_code=404, detail="Clothing item not found.")
        return {"mesaj": "Clothing item updated", "message": "Clothing item updated", "id": item_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating clothing item: {str(e)}")


@router.patch("/items/{item_id}/laundry")
def set_laundry_status(item_id: int, request: LaundryStatusRequest, db: sqlite3.Connection = Depends(get_db)):
    """Quickly toggle laundry (dirty/clean) status of a clothing item."""
    repo = ItemRepository(db)
    updated = repo.update_cloth(item_id=item_id, temiz=not request.is_dirty)
    if not updated:
        raise HTTPException(status_code=404, detail="Clothing item not found.")
    return {"message": "Laundry status updated", "id": item_id, "is_dirty": request.is_dirty}


@router.patch("/items/{item_id}/favorite")
def set_favorite_status(item_id: int, request: FavoriteStatusRequest, db: sqlite3.Connection = Depends(get_db)):
    """Quickly toggle favorite status of a clothing item."""
    repo = ItemRepository(db)
    updated = repo.update_cloth(item_id=item_id, is_favorite=request.is_favorite)
    if not updated:
        raise HTTPException(status_code=404, detail="Clothing item not found.")
    return {"message": "Favorite status updated", "id": item_id, "is_favorite": request.is_favorite}


@router.delete("/items/{item_id}")
def delete_cloth(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Deletes a clothing item."""
    repo = ItemRepository(db)
    try:
        deleted = repo.delete_cloth(item_id=item_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Clothing item not found.")
        return {"mesaj": "Clothing item deleted", "message": "Clothing item deleted", "id": item_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting clothing item: {str(e)}")


@router.post("/chat")
def chat(request: ChatRequest, db: sqlite3.Connection = Depends(get_db)):
    """Handles AI Stylist chat messages."""
    repo = ItemRepository(db)
    history = repo.get_chat_history(request.user_id)
    
    context_message = request.mesaj
    if request.hava_durumu:
        context_message = f"[System Note: Current weather at location is '{request.hava_durumu}']\nUser: {request.mesaj}"

    try:
        result = ollama_client.get_chat_response(history, context_message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
        
    repo.save_chat_message(request.user_id, "user", request.mesaj)
    repo.save_chat_message(request.user_id, "assistant", result.get("asistan_mesaji", ""))
    return result


@router.get("/chat/history/{user_id}")
def chat_history(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Returns chat history for a user."""
    repo = ItemRepository(db)
    return repo.get_chat_history(user_id)


@router.post("/outfit/suggest")
def recommend_outfit(request: OutfitRecommendRequest, db: sqlite3.Connection = Depends(get_db)):
    """Generates AI outfit recommendation."""
    repo = ItemRepository(db)
    clean_clothes = repo.get_clothes(request.user_id, clean_only=True)
    
    if not clean_clothes:
        raise HTTPException(status_code=400, detail="No clean clothes available.")
        
    context = {
        "etkinlik": request.etkinlik,
        "hava_durumu": request.hava_durumu,
        "stil_tercihi": request.stil_tercihi or "",
    }
    
    try:
        result = ollama_client.generate_outfit_recommendation(context, clean_clothes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")
        
    selected_ids = result.get("secilen_kiyafet_idleri", [])
    valid_ids = {c["id"] for c in clean_clothes}
    selected_ids = [i for i in selected_ids if i in valid_ids]
    
    recommendation_id = repo.save_outfit_recommendation(
        user_id=request.user_id,
        context_json=json.dumps(context, ensure_ascii=False),
        item_ids=selected_ids,
        description=result.get("aciklama", ""),
    )
    
    selected_clothes_detail = [c for c in clean_clothes if c["id"] in selected_ids]
    
    return {
        "id": recommendation_id,
        "aciklama": result.get("aciklama", ""),
        "description": result.get("aciklama", ""),
        "secilen_kiyafetler": selected_clothes_detail,
        "selected_items": selected_clothes_detail,
    }


@router.get("/outfits/{user_id}")
def list_outfits(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Lists saved outfit recommendations."""
    repo = ItemRepository(db)
    return repo.get_outfit_recommendations(user_id)


@router.post("/outfit/manual")
def create_manual_outfit(request: ManualOutfitCreateRequest, db: sqlite3.Connection = Depends(get_db)):
    """Creates a user-defined manual outfit."""
    repo = ItemRepository(db)
    context = {"etkinlik": "Manuel Kombin", "hava_durumu": "Belirtilmedi"}
    outfit_id = repo.save_outfit_recommendation(
        user_id=request.user_id,
        context_json=json.dumps(context, ensure_ascii=False),
        item_ids=request.item_ids,
        description=request.aciklama
    )
    return {"id": outfit_id, "mesaj": "Outfit created", "message": "Outfit created"}


@router.post("/analyze-image")
def analyze_cloth_image(request: AnalyzeClothRequest):
    """
    Kıyafet görselini AI ile analiz eder.
    FashionSigLIP → 6 özellik (tür, renk, desen, malzeme, mevsim, kullanım)
    + Moondream → zengin kıyafet açıklaması (kombin_notu için kullanılabilir)
    Tüm yanıtlar Türkçe düz metin — kullanıcı JSON görmez.
    """
    import base64 as _b64
    import httpx as _httpx

    image_url = request.gorsel_url
    if not image_url:
        raise HTTPException(status_code=400, detail="gorsel_url is required.")

    # Görseli base64'e çevir
    image_b64: Optional[str] = None
    try:
        if image_url.startswith("http://") or image_url.startswith("https://"):
            filename = image_url.split("/")[-1]
            for candidate in [
                Path("static/uploads") / filename,
                Path("uploads") / filename,
            ]:
                if candidate.exists():
                    image_b64 = _b64.b64encode(candidate.read_bytes()).decode()
                    break
            if not image_b64:
                with _httpx.Client(timeout=15.0) as c:
                    r = c.get(image_url)
                    r.raise_for_status()
                image_b64 = _b64.b64encode(r.content).decode()
        else:
            p = Path(image_url)
            if p.exists():
                image_b64 = _b64.b64encode(p.read_bytes()).decode()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Görsel alınamadı: {e}")

    if not image_b64:
        raise HTTPException(status_code=400, detail="Görsel yüklenemedi.")

    # FashionSigLIP — 6 özellik
    attrs = fashion_classifier.classify_all_attributes(image_b64=image_b64)

    if not attrs.get("success"):
        # Fallback: eski 4-özellik metodu
        attrs = fashion_classifier.classify_image(image_b64=image_b64)
        if not attrs.get("success"):
            raise HTTPException(
                status_code=503,
                detail=f"AI model hatası: {attrs.get('error', 'Bilinmeyen hata')}"
            )
        return {
            "tur":          attrs.get("tur", ""),
            "renk":         attrs.get("renk", ""),
            "desen":        "düz",
            "malzeme":      attrs.get("kumas", ""),
            "mevsim":       attrs.get("mevsim", "tüm sezon"),
            "kullanim":     attrs.get("stil_etiketi", "günlük kullanım"),
            "stil_etiketi": attrs.get("stil_etiketi", ""),
            "post_category": attrs.get("post_category", ""),
            "guven_skoru":  attrs.get("confidence", 0.0),
        }

    def _best(attr: str, fallback: str = "") -> str:
        v = attrs.get(attr)
        if isinstance(v, dict):
            return v.get("best", fallback)
        return str(v) if v else fallback

    return {
        # Gardrop formu için doğrudan kullanılabilir alanlar (düz Türkçe)
        "tur":          _best("category", "bilinmiyor"),
        "renk":         _best("color", "bilinmiyor"),
        "desen":        _best("pattern", "düz"),
        "malzeme":      _best("material", "bilinmiyor"),
        "mevsim":       _best("season", "tüm sezon"),
        "kullanim":     _best("occasion", "günlük kullanım"),
        "stil_etiketi": _best("occasion", "gündelik"),
        "post_category": attrs.get("post_category", ""),
        "guven_skoru":  round(
            attrs.get("category", {}).get("confidence", 0.0)
            if isinstance(attrs.get("category"), dict) else 0.0,
            2
        ),
        # Alternatifler (Flutter'da dropdown için)
        "alternatif_turler": [
            t["label"] for t in (
                attrs.get("category", {}).get("top_3", [])
                if isinstance(attrs.get("category"), dict) else []
            )
        ],
        "alternatif_renkler": [
            t["label"] for t in (
                attrs.get("color", {}).get("top_3", [])
                if isinstance(attrs.get("color"), dict) else []
            )
        ],
    }



@router.delete("/outfits/{outfit_id}")
def delete_outfit(outfit_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Deletes an outfit recommendation."""
    repo = ItemRepository(db)
    try:
        deleted = repo.delete_outfit(outfit_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Outfit not found.")
        return {"mesaj": "Outfit deleted", "message": "Outfit deleted", "id": outfit_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting outfit: {str(e)}")


# Backwards compatibility function aliases
kiyafet_ekle = add_cloth
kiyafetleri_listele = list_clothes
kiyafet_guncelle = update_cloth
kiyafet_sil = delete_cloth
kombin_oner = recommend_outfit
outfits_listele = list_outfits
manuel_kombin_olustur = create_manual_outfit
kiyafet_gorseli_analiz_et = analyze_cloth_image
kombin_sil = delete_outfit
