"""
Pydantic v2 modelleri — Request & Response şemaları.
Python 3.9 uyumlu (Optional kullanımı).
"""
from __future__ import annotations

from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional, List, Dict


# ============================================================
# Request Modelleri
# ============================================================

class UserRegisterRequest(BaseModel):
    """Kayıt isteği."""
    email: EmailStr
    password: str


class UserLoginRequest(BaseModel):
    """Giriş isteği."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Kayıt veya Giriş başarılı olduğunda dönülecek yanıt."""
    user_id: str
    message: str


class PasswordResetRequest(BaseModel):
    """Şifre sıfırlama isteği."""
    email: EmailStr
    new_password: str


class PasswordResetCodeRequest(BaseModel):
    """Şifre sıfırlama kodu talep isteği."""
    email: EmailStr


class PasswordResetVerifyRequest(BaseModel):
    """Şifre sıfırlama kodu doğrulama isteği."""
    email: EmailStr
    code: str


class ProfileUpdateRequest(BaseModel):
    """Profil güncelleme isteği."""
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    chest: Optional[str] = None
    waist: Optional[str] = None
    hips: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None

class RequestEmailChangeRequest(BaseModel):
    new_email: EmailStr

class VerifyEmailChangeRequest(BaseModel):
    new_email: EmailStr
    code: str

class RequestPasswordChangeRequest(BaseModel):
    pass # Uses auth header to send to current email

class VerifyPasswordChangeRequest(BaseModel):
    new_password: str
    code: str


class PrivacySettingsRequest(BaseModel):
    """Gizlilik ayarları güncelleme isteği."""
    profile_visibility: Literal["public", "private"] = "public"


class PostCreate(BaseModel):
    """Yeni post oluşturma isteği."""
    user_id: str
    image_url: str
    caption: Optional[str] = None
    outfit_items: List[str] = Field(default_factory=list)
    visibility: Literal["public", "followers", "private"] = "public"
    ai_training_consent: bool = False


class PostUpdateRequest(BaseModel):
    """Var olan postu güncelleme isteği."""
    caption: Optional[str] = None
    visibility: Optional[Literal["public", "followers", "private"]] = None
    outfit_items: Optional[List[str]] = None
    ai_training_consent: Optional[bool] = None


class FollowRequest(BaseModel):
    """Takip etme / takipten çıkma isteği."""
    follower_id: str
    following_id: str


class LikeRequest(BaseModel):
    """Beğeni isteği."""
    user_id: str


class SaveRequest(BaseModel):
    """Kaydetme isteği."""
    user_id: str


class CommentRequest(BaseModel):
    """Yorum yapma isteği."""
    user_id: str
    content: str


class CaptionRequest(BaseModel):
    """AI caption önerisi isteği."""
    outfit_items: List[Dict] = Field(default_factory=list)
    style_hint: str = ""
    image_url: Optional[str] = None  # Görsel URL'si — Gemini Vision için


# ============================================================
# Response Modelleri
# ============================================================

class UserResponse(BaseModel):
    """Kullanıcı profil bilgisi."""
    user_id: str
    email: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    followers_count: int = 0
    following_count: int = 0
    created_at: str
    is_following: bool = False
    profile_visibility: str = "public"
    height: Optional[str] = None
    weight: Optional[str] = None
    chest: Optional[str] = None
    waist: Optional[str] = None
    hips: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None
    active_title: Optional[str] = None


class OutfitItemResponse(BaseModel):
    """Post'a bağlı kombin parçası."""
    item_id: str
    category: str
    image_url: Optional[str] = None


class CommentResponse(BaseModel):
    """Yorum yanıtı."""
    comment_id: str
    post_id: str
    user_id: str
    username: str
    avatar_url: Optional[str] = None
    content: str
    created_at: str


class PostResponse(BaseModel):
    """Tek bir post."""
    post_id: str
    user_id: str
    username: str = ""
    display_name: str = ""
    avatar_url: Optional[str] = None
    active_title: Optional[str] = None
    image_url: str
    caption: Optional[str] = None
    visibility: str = "public"
    ai_training_consent: bool = False
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    is_saved: bool = False
    outfit_items: List[OutfitItemResponse] = Field(default_factory=list)
    created_at: str


class FeedResponse(BaseModel):
    """Sayfalandırılmış feed yanıtı."""
    posts: List[PostResponse]
    next_cursor: Optional[str] = None


class UserStatsResponse(BaseModel):
    """Kullanıcı istatistikleri."""
    user_id: str
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0


class MessageResponse(BaseModel):
    """Genel başarı/hata mesajı."""
    success: bool
    message: str
    data: Optional[Dict] = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str


# ============================================================
# 2FA Şemaları
# ============================================================

class TwoFASetupResponse(BaseModel):
    """2FA kurulum yanıtı — OTP URI ve secret döner."""
    secret: str
    otpauth_uri: str
    message: str


class TwoFAVerifyRequest(BaseModel):
    """2FA kodu doğrulama isteği."""
    user_id: str
    code: str


class TwoFALoginRequest(BaseModel):
    """Login sırasında 2FA kodu doğrulama."""
    user_id: str
    code: str


class TwoFAStatusResponse(BaseModel):
    """Kullanıcının 2FA durumu."""
    user_id: str
    two_fa_enabled: bool


class PasswordResetWithTokenRequest(BaseModel):
    """Token tabanlı şifre sıfırlama (gelecek için hazır)."""
    email: str
    new_password: str
    confirm_password: str
