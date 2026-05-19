from pydantic import BaseModel
from datetime import datetime


class MenuCreate(BaseModel):
    name: str
    path: str | None = None
    icon: str | None = None
    order: int = 0


class MenuUpdate(BaseModel):
    name: str | None = None
    path: str | None = None
    icon: str | None = None
    order: int | None = None
    is_active: bool | None = None


class MenuOut(BaseModel):
    id: int
    name: str
    path: str | None
    icon: str | None
    order: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}