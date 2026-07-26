"""
Dijital Gardrop — FastAPI ana uygulama.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.routers import posts, feed, follows, users, auth, wardrobe, search
from app.api.routers import likes 
from app.services.ollama_caption_service import router as captions_router
from app.services.fashion_classifier import load_model_on_startup

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "uploads").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatılırken veritabanını oluşturur ve FashionSigLIP modelini yükler."""
    init_db()
    # FashionSigLIP — Kıyafet sınıflandırma modelini bellekte hazırla
    import asyncio
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, load_model_on_startup)
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
app.include_router(likes.router,  tags=["Likes"])  
app.include_router(feed.router, tags=["Feed"])
app.include_router(follows.router, tags=["Follows"])
app.include_router(users.router,     prefix="/users",    tags=["Users"])
app.include_router(search.router,    prefix="/search",      tags=["Search"])
app.include_router(wardrobe.router,  prefix="/wardrobe", tags=["Wardrobe"])
app.include_router(captions_router,  prefix="/captions", tags=["Captions"])


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "dijital-gardrop-api", "version": "1.0.0"}
