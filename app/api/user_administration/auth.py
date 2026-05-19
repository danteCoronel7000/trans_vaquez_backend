from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from jose import JWTError
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.dependencies.db import get_db
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.exceptions.http_exceptions import UnauthorizedException

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = UserRepository(db).get_by_username(data.username)
    if not user or not verify_password(data.password, user.password):
        raise UnauthorizedException("Credenciales incorrectas")
    payload = {"sub": str(user.id)}
    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Token de refresco inválido")
        user_payload = {"sub": payload["sub"]}
        return TokenResponse(
            access_token=create_access_token(user_payload),
            refresh_token=create_refresh_token(user_payload),
        )
    except JWTError:
        raise UnauthorizedException("Token expirado o inválido")