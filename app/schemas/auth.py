from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.person import PersonOut


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    person:        Optional[PersonOut] = None  # 👈 esto faltaba


class RefreshRequest(BaseModel):
    refresh_token: str

# ── Nuevo ──────────────────────────────────────────────
class ImageInfo(BaseModel):
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PersonInfo(BaseModel):
    id:         int
    first_name: str
    last_name:  str
    ci:         str
    gender:     str
    birth_date: str
    phone:      Optional[str] = None
    address:    Optional[str] = None
    city:       Optional[str] = None
    country:    Optional[str] = None
    gmail:      Optional[str] = None
    image:      Optional[ImageInfo] = None

    model_config = ConfigDict(from_attributes=True)