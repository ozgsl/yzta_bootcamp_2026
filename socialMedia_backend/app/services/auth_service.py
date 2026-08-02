import hashlib
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth import RefreshToken, VerificationCode
from app.models.social import Profile
from app.services.providers.cache_provider import CacheProvider, InMemoryCacheProvider

logger = logging.getLogger(__name__)

# Basic settings for JWT (in production, use env vars)
SECRET_KEY = "super-secret-production-key-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Handles Production Authentication Logic (JWT, Bcrypt, Refresh Tokens, Email Verification).
    """
    def __init__(self, db: Session, cache: CacheProvider = None):
        self.db = db
        self.cache = cache or InMemoryCacheProvider()

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        if not hashed_password:
            return False
        # Fallback for old plain-text passwords during migration
        if not hashed_password.startswith("$2b$"):
            return plain_password == hashed_password
        return pwd_context.verify(plain_password, hashed_password)

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def register(self, email: str, password: str) -> str:
        existing = self.db.scalars(select(Profile).where(Profile.email == email)).first()
        if existing:
            raise ValueError("Bu e-posta adresi zaten kullanılıyor.")
            
        hashed_password = self.get_password_hash(password)
        new_user = Profile(email=email, password_hash=hashed_password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return str(new_user.id)

    def login(self, email: str, password: str, device: str = None, ip: str = None) -> tuple[str, str, str]:
        """Returns (access_token, refresh_token_plain, user_id)."""
        user = self.db.scalars(select(Profile).where(Profile.email == email)).first()
        if not user or not self.verify_password(password, user.password_hash):
            raise ValueError("E-posta veya şifre hatalı.")
            
        # Create Access Token
        access_token = self.create_access_token(data={"sub": str(user.id)})
        
        # Create Refresh Token
        refresh_token_plain = f"rt_{random.getrandbits(128):032x}"
        rt_hash = self.hash_token(refresh_token_plain)
        
        rt = RefreshToken(
            user_id=user.id,
            token_hash=rt_hash,
            device=device,
            ip=ip,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(rt)
        self.db.commit()
        
        return access_token, refresh_token_plain, str(user.id)

    def google_login(self, email: str, display_name: str = None, avatar_url: str = None, device: str = None, ip: str = None) -> tuple[str, str, str]:
        """Handles Google OAuth login or automatic profile registration. Returns (access_token, refresh_token_plain, user_id)."""
        user = self.db.scalars(select(Profile).where(Profile.email == email)).first()
        if not user:
            clean_name = (display_name or email.split('@')[0]).lower().replace(" ", "_")[:20]
            new_username = f"{clean_name}_{random.getrandbits(32):08x}"
            user = Profile(
                email=email,
                password_hash=None,
                username=new_username,
                display_name=display_name or email.split('@')[0],
                avatar_url=avatar_url
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        elif avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
            self.db.commit()

        # Create Access Token
        access_token = self.create_access_token(data={"sub": str(user.id)})
        
        # Create Refresh Token
        refresh_token_plain = f"rt_{random.getrandbits(128):032x}"
        rt_hash = self.hash_token(refresh_token_plain)
        
        rt = RefreshToken(
            user_id=user.id,
            token_hash=rt_hash,
            device=device,
            ip=ip,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(rt)
        self.db.commit()
        
        return access_token, refresh_token_plain, str(user.id)

    def refresh(self, old_refresh_token_plain: str, device: str = None, ip: str = None) -> tuple[str, str, str]:
        """Refresh Token Rotation."""
        rt_hash = self.hash_token(old_refresh_token_plain)
        
        rt = self.db.scalars(select(RefreshToken).where(RefreshToken.token_hash == rt_hash)).first()
        if not rt:
            raise ValueError("Geçersiz Refresh Token.")
            
        if rt.revoked_at or rt.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh Token süresi dolmuş veya iptal edilmiş.")
            
        # Revoke old token (Rotation)
        rt.revoked_at = datetime.now(timezone.utc)
        self.db.commit()
        
        # Create new pair
        access_token = self.create_access_token(data={"sub": str(rt.user_id)})
        
        new_refresh_token_plain = f"rt_{random.getrandbits(128):032x}"
        new_rt_hash = self.hash_token(new_refresh_token_plain)
        
        new_rt = RefreshToken(
            user_id=rt.user_id,
            token_hash=new_rt_hash,
            device=device,
            ip=ip,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(new_rt)
        self.db.commit()
        
        return access_token, new_refresh_token_plain, str(rt.user_id)

    def logout(self, refresh_token_plain: str):
        rt_hash = self.hash_token(refresh_token_plain)
        rt = self.db.scalars(select(RefreshToken).where(RefreshToken.token_hash == rt_hash)).first()
        if rt:
            rt.revoked_at = datetime.now(timezone.utc)
            self.db.commit()

    def request_password_reset(self, email: str) -> dict[str, Any]:
        user = self.db.scalars(select(Profile).where(Profile.email == email)).first()
        if not user:
            return {'success': True, 'message': 'Eğer bu e-posta adresi sistemimizde kayıtlıysa, şifre sıfırlama kodu gönderildi.'}
            
        code_plain = str(random.randint(100000, 999999))
        code_hash = self.hash_token(code_plain)
        
        vc = VerificationCode(
            email=email,
            code_hash=code_hash,
            purpose="password_reset",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
        )
        self.db.add(vc)
        self.db.commit()
        
        logger.info(f"[RESET CODE] Email: {email} -> Code: {code_plain}")
        return {'success': True, 'message': 'Şifre sıfırlama kodu gönderildi.', 'debug_code': code_plain}
