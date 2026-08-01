"""
Dijital Gardrop — FastAPI ana uygulama.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routers import (
    analytics,
    auth,
    feed,
    follows,
    likes,
    notifications,
    posts,
    search,
    users,
    wardrobe,
)
from app.models.base import Base, engine
from app.models.outfit import *

# Import all models to ensure they are registered before create_all
from app.models.social import *
from app.models.wardrobe import *
from app.services.fashion_classifier import load_model_on_startup
from app.services.ollama_caption_service import (
    OLLAMA_BASE_URL,
    OLLAMA_TEXT_MODEL,
    OLLAMA_VISION_MODEL,
)
from app.services.ollama_caption_service import router as captions_router

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "uploads").mkdir(exist_ok=True)


async def _warmup_ollama_models():
    """
    Backend başladıktan sonra arka planda LLaVA ve llama3.2'yi belleğe yükler.
    keep_alive=10m ile model 10 dakika bellekte kalır — sonraki istekler hızlı olur.
    """
    import asyncio

    import httpx

    await asyncio.sleep(4)  # Backend tamamen başlayana kadar bekle

    async with httpx.AsyncClient(timeout=120.0) as client:
        # LLaVA warm-up
        try:
            await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_VISION_MODEL,
                    "prompt": "Hi",
                    "stream": False,
                    "keep_alive": "10m",
                    "options": {"num_predict": 1},
                },
            )
            print(f"[Warm-up] ✅ LLaVA ({OLLAMA_VISION_MODEL}) belleğe yüklendi.")
        except Exception as e:
            print(f"[Warm-up] ⚠️ LLaVA yüklenemedi: {e}")

        # llama3.2 warm-up
        try:
            await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_TEXT_MODEL,
                    "prompt": "Hi",
                    "stream": False,
                    "keep_alive": "10m",
                    "options": {"num_predict": 1},
                },
            )
            print(f"[Warm-up] ✅ Ollama ({OLLAMA_TEXT_MODEL}) belleğe yüklendi.")
        except Exception as e:
            print(f"[Warm-up] ⚠️ Ollama yüklenemedi: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatılırken veritabanını oluşturur, FashionSigLIP ve LLaVA modellerini ön-ısıtır."""
    pass  # Base.metadata.create_all(bind=engine)
    import asyncio
    loop = asyncio.get_event_loop()
    # FashionSigLIP — Kıyafet sınıflandırma modelini bellekte hazırla
    await loop.run_in_executor(None, load_model_on_startup)
    # LLaVA + Ollama — Arka planda modelleri belleğe yükle (warm-up)
    asyncio.create_task(_warmup_ollama_models())
    yield


app = FastAPI(
    title="Dijital Gardrop API",
    description="Dijital Gardrop sosyal medya modülü REST API'si",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Router'ları dahil et
app.include_router(auth.router,      prefix="/auth",     tags=["Auth"])
app.include_router(posts.router,     prefix="/posts",    tags=["Posts"])
app.include_router(likes.router,     prefix="/likes",    tags=["Likes"])
app.include_router(feed.router, prefix="/feed", tags=["Feed"])
app.include_router(follows.router, tags=["Follows"])
app.include_router(users.router,     prefix="/users",    tags=["Users"])
app.include_router(search.router,    prefix="/search",      tags=["Search"])
app.include_router(wardrobe.router,  prefix="/wardrobe", tags=["Wardrobe"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(analytics.router,      prefix="/analytics",      tags=["Analytics"])
app.include_router(captions_router,  prefix="/captions", tags=["Captions"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "dijital-gardrop-api", "version": "1.0.0"}
