"""
Uygulama yapılandırması — Pydantic BaseSettings ile .env okuma.

Tüm yollar Path(__file__) ile hesaplanır — platform bağımsızdır (Mac/Windows/Linux).
.env dosyası ile override edilebilir.
"""

from pathlib import Path

from pydantic_settings import BaseSettings

# Proje kökü: config.py → core → app → socialMedia_backend
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Veritabanı: proje kökünde, platform bağımsız relative path
    DATABASE_PATH: str = str(_PROJECT_ROOT / "dijital_gardrop.db")

    # AI Servisleri
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    FIREBASE_BUCKET: str | None = None

    # CORS — geliştirme ortamında tüm yerel ağlara izin ver
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:8081,"
        "http://localhost:8080,"
        "http://10.0.2.2:8081,"   # Android emülatör
        "http://127.0.0.1:8081"
    )

    # Sunucu
    SERVER_HOST: str = "localhost"
    SERVER_PORT: str = "8000"

    @property
    def cors_origins_list(self) -> list[str]:
        """Virgülle ayrılmış CORS origin'lerini listeye çevirir."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def project_root(self) -> Path:
        return _PROJECT_ROOT

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
