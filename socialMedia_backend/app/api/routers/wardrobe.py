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
class KiyafetEkleIstek(BaseModel):
    tur: str
    renk: str
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

class ChatIstek(BaseModel):
    user_id: str
    mesaj: str
    hava_durumu: Optional[str] = None

class KombinOnerIstek(BaseModel):
    user_id: str
    etkinlik: str
    hava_durumu: str
    stil_tercihi: Optional[str] = ""

class ManualOutfitCreateRequest(BaseModel):
    user_id: str
    item_ids: List[int]
    aciklama: str

# --- Endpoints ---
@router.post("/items")
def kiyafet_ekle(user_id: str, istek: KiyafetEkleIstek, db: sqlite3.Connection = Depends(get_db)):
    repo = ItemRepository(db)
    veri = istek.model_dump()
    kiyafet_id = repo.kiyafet_ekle(user_id=user_id, **veri)
    return {"id": kiyafet_id, "mesaj": "Kıyafet eklendi"}

@router.get("/items/{user_id}")
def kiyafetleri_listele(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    repo = ItemRepository(db)
    return repo.kiyafetleri_getir(user_id)

@router.put("/items/{item_id}")
def kiyafet_guncelle(item_id: int, istek: KiyafetEkleIstek, db: sqlite3.Connection = Depends(get_db)):
    """Mevcut bir kıyafeti günceller."""
    repo = ItemRepository(db)
    veri = istek.model_dump()
    try:
        updated = repo.kiyafet_guncelle(kiyafet_id=item_id, **veri)
        if not updated:
            raise HTTPException(status_code=404, detail="Kıyafet bulunamadı.")
        return {"mesaj": "Kıyafet güncellendi", "id": item_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kıyafet güncellenirken hata: {str(e)}")

@router.delete("/items/{item_id}")
def kiyafet_sil(item_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Bir kıyafeti siler."""
    repo = ItemRepository(db)
    try:
        deleted = repo.kiyafet_sil(kiyafet_id=item_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Kıyafet bulunamadı.")
        return {"mesaj": "Kıyafet silindi", "id": item_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kıyafet silinirken hata: {str(e)}")

@router.post("/chat")
def chat(istek: ChatIstek, db: sqlite3.Connection = Depends(get_db)):
    repo = ItemRepository(db)
    gecmis = repo.sohbet_gecmisini_getir(istek.user_id)
    
    baglamli_mesaj = istek.mesaj
    if istek.hava_durumu:
        baglamli_mesaj = f"[Sistem Notu: Kullanıcının bulunduğu konumda güncel hava durumu '{istek.hava_durumu}']\nKullanıcı: {istek.mesaj}"

    try:
        sonuc = ollama_client.sohbet_yaniti_al(gecmis, baglamli_mesaj)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI hatası: {e}")
        
    repo.mesaj_kaydet(istek.user_id, "user", istek.mesaj)
    repo.mesaj_kaydet(istek.user_id, "assistant", sonuc["asistan_mesaji"])
    return sonuc


@router.get("/chat/history/{user_id}")
def chat_history(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Kullanıcının sohbet geçmişini döndürür."""
    repo = ItemRepository(db)
    return repo.sohbet_gecmisini_getir(user_id)

@router.post("/outfit/suggest")
def kombin_oner(istek: KombinOnerIstek, db: sqlite3.Connection = Depends(get_db)):
    repo = ItemRepository(db)
    temiz_kiyafetler = repo.kiyafetleri_getir(istek.user_id, sadece_temiz=True)
    
    if not temiz_kiyafetler:
        raise HTTPException(status_code=400, detail="Temiz kıyafetin yok.")
        
    baglam = {
        "etkinlik": istek.etkinlik,
        "hava_durumu": istek.hava_durumu,
        "stil_tercihi": istek.stil_tercihi or "",
    }
    
    try:
        sonuc = ollama_client.kombin_onerisi_uret(baglam, temiz_kiyafetler)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API hatası: {e}")
        
    secilen_idler = sonuc["secilen_kiyafet_idleri"]
    gecerli_idler = {k["id"] for k in temiz_kiyafetler}
    secilen_idler = [i for i in secilen_idler if i in gecerli_idler]
    
    oneri_id = repo.kombin_onerisi_kaydet(
        user_id=istek.user_id,
        baglam_json=json.dumps(baglam, ensure_ascii=False),
        kiyafet_idleri=secilen_idler,
        aciklama=sonuc["aciklama"],
    )
    
    secilen_kiyafetler_detay = [k for k in temiz_kiyafetler if k["id"] in secilen_idler]
    
    return {
        "oneri_id": oneri_id,
        "secilen_kiyafetler": secilen_kiyafetler_detay,
        "aciklama": sonuc["aciklama"],
    }

@router.get("/outfits/{user_id}")
def outfits_listele(user_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Kullanıcının daha önce oluşturduğu kombinleri getirir."""
    repo = ItemRepository(db)
    return repo.kombin_onerilerini_getir(user_id)

@router.post("/outfits/")
def manuel_kombin_olustur(istek: ManualOutfitCreateRequest, db: sqlite3.Connection = Depends(get_db)):
    """Kullanıcının manuel olarak seçtiği kıyafetlerden kombin oluşturur."""
    repo = ItemRepository(db)
    baglam_json = json.dumps({"type": "manual"})
    oneri_id = repo.kombin_onerisi_kaydet(
        user_id=istek.user_id,
        baglam_json=baglam_json,
        kiyafet_idleri=istek.item_ids,
        aciklama=istek.aciklama,
    )
    return {"oneri_id": oneri_id, "mesaj": "Kombin başarıyla kaydedildi."}


# ---------------------------------------------------------------------------
# FashionSigLIP — Kıyafet Formu Otomatik Doldurma
# ---------------------------------------------------------------------------

class AnalyzeKiyafetIstek(BaseModel):
    """
    Görsel URL veya base64 alır; FashionSigLIP ile analiz eder.
    Frontend'in 'Otomatik Doldur' butonu bu endpoint'i kullanır.
    """
    image_url: Optional[str] = None
    image_b64: Optional[str] = None


@router.post("/items/analyze")
def kiyafet_gorseli_analiz_et(istek: AnalyzeKiyafetIstek):
    """
    Kıyafet görselini FashionSigLIP ile analiz eder.

    Dönen alanlar doğrudan KiyafetEkleIstek modeline karşılık gelir:
    - tur           → tişört, pantolon, elbise ...
    - renk          → siyah, beyaz, mavi ...
    - stil_etiketi  → gündelik, şık, spor ...
    - mevsim        → yaz, kış, tüm sezon ...
    - post_category → üst giyim, alt giyim, ayakkabı, aksesuar, dış giyim, diğer

    Model yüklü değilse success=False + açıklayıcı hata döner.
    """
    if not fashion_classifier.is_ready:
        return {
            "success": False,
            "message": "FashionSigLIP modeli henüz yüklenmedi veya yüklenemedi.",
            "data": None,
        }

    # --- Görsel kaynağı belirle ---
    image_b64 = istek.image_b64
    image_path: Optional[Path] = None

    if not image_b64 and istek.image_url:
        # Yerel static/uploads dosyası mı?
        if "static/uploads/" in istek.image_url:
            from app.services.ollama_caption_service import UPLOADS_DIR
            filename = istek.image_url.split("static/uploads/")[-1].split("?")[0]
            local = UPLOADS_DIR / filename
            if local.exists():
                image_path = local
            else:
                # URL üzerinden indir
                try:
                    import httpx
                    with httpx.Client(timeout=10) as client:
                        resp = client.get(istek.image_url)
                        resp.raise_for_status()
                        import base64 as b64lib
                        image_b64 = b64lib.b64encode(resp.content).decode()
                except Exception as e:
                    return {"success": False, "message": f"Görsel indirilemedi: {e}"}
        else:
            # Harici URL — indir
            try:
                import httpx, base64 as b64lib
                with httpx.Client(timeout=10) as client:
                    resp = client.get(istek.image_url)
                    resp.raise_for_status()
                    image_b64 = b64lib.b64encode(resp.content).decode()
            except Exception as e:
                return {"success": False, "message": f"Görsel indirilemedi: {e}"}

    if not image_b64 and image_path is None:
        return {
            "success": False,
            "message": "image_url veya image_b64 sağlanmalı.",
        }

    result = fashion_classifier.classify_image(
        image_path=image_path,
        image_b64=image_b64,
    )

    if not result.get("success"):
        return {
            "success": False,
            "message": result.get("error", "Sınıflandırma başarısız."),
            "data": None,
        }

    return {
        "success": True,
        "message": "Kıyafet analizi tamamlandı.",
        "data": {
            "tur": result["tur"],
            "renk": result["renk"],
            "stil_etiketi": result["stil_etiketi"],
            "mevsim": result["mevsim"],
            "post_category": result["post_category"],
            "confidence": result["confidence"],
            "alternatifler": result.get("alternatifler", []),
        },
    }


