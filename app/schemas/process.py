from pydantic import BaseModel
from datetime import datetime


class ProcessCreate(BaseModel):
    name: str
    code: str
    description: str | None = None


class ProcessUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class ProcessOut(BaseModel):
    id: int
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}