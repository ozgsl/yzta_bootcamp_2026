
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.domain.schemas import (
    PasswordResetCodeRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.models.base import get_db
from app.services.auth_service import AuthService

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str | None = None
    token_type: str = "bearer"
    
class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class GoogleLoginRequest(BaseModel):
    id_token: str | None = None
    email: str
    display_name: str | None = None
    avatar_url: str | None = None

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(request: UserRegisterRequest, req: Request, service: AuthService = Depends(get_auth_service)):
    try:
        service.register(request.email, request.password)
        # Login directly after register
        access_token, refresh_token, user_id = service.login(
            request.email, 
            request.password, 
            device=req.headers.get("User-Agent"), 
            ip=req.client.host if req.client else None
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, req: Request, service: AuthService = Depends(get_auth_service)):
    try:
        access_token, refresh_token, user_id = service.login(
            request.email, 
            request.password,
            device=req.headers.get("User-Agent"), 
            ip=req.client.host if req.client else None
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/google", response_model=TokenResponse)
def google_login(request: GoogleLoginRequest, req: Request, service: AuthService = Depends(get_auth_service)):
    try:
        access_token, refresh_token, user_id = service.google_login(
            email=request.email,
            display_name=request.display_name or request.email.split("@")[0],
            avatar_url=request.avatar_url,
            device=req.headers.get("User-Agent"),
            ip=req.client.host if req.client else None
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, req: Request, service: AuthService = Depends(get_auth_service)):
    try:
        access_token, refresh_token, user_id = service.refresh(
            request.refresh_token,
            device=req.headers.get("User-Agent"), 
            ip=req.client.host if req.client else None
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token, user_id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
def logout(request: LogoutRequest, service: AuthService = Depends(get_auth_service)):
    service.logout(request.refresh_token)
    return {"message": "Başarıyla çıkış yapıldı."}

@router.post('/request-password-reset')
def request_password_reset(request: PasswordResetCodeRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.request_password_reset(request.email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
