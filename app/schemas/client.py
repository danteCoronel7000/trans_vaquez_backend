from pydantic import BaseModel
from datetime import datetime
from app.schemas.person import PersonOut


class ClientCreate(BaseModel):
    person_id: int
    nit:          str | None = None
    razon_social: str | None = None


class ClientUpdate(BaseModel):
    is_active: bool | None = None
    nit:          str | None = None
    razon_social: str | None = None


class ClientOut(BaseModel):
    id:        int
    person_id: int
    nit:          str | None = None
    razon_social: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientDetailOut(BaseModel):
    id:        int
    is_active: bool
    nit:          str | None = None
    razon_social: str | None = None
    created_at: datetime
    person:    PersonOut

    model_config = {"from_attributes": True}