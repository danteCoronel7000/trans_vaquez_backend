from pydantic import BaseModel
from datetime import datetime


class UserSystemOut(BaseModel):
    id:                  int
    person_id:           int
    is_active:           bool
    fecha_ultimo_acceso: datetime | None

    model_config = {"from_attributes": True}