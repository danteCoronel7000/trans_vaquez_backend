from pydantic import BaseModel
from datetime import datetime
from app.models.chofer import CategoriaEnum
from app.schemas.person import PersonOut


class ChoferCreate(BaseModel):
    person_id: int
    licencia:  str
    categoria: CategoriaEnum


class ChoferUpdate(BaseModel):
    licencia:  str | None = None
    categoria: CategoriaEnum | None = None
    is_active: bool | None = None


class ChoferOut(BaseModel):
    id:        int
    person_id: int
    licencia:  str
    categoria: CategoriaEnum
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChoferDetailOut(BaseModel):
    id:        int
    licencia:  str
    categoria: CategoriaEnum
    is_active: bool
    created_at: datetime
    person:    PersonOut

    model_config = {"from_attributes": True}