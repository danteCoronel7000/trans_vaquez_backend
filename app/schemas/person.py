from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
from app.models.person import GenderEnum


class PersonCreate(BaseModel):
    first_name: str
    last_name:  str
    ci:         str
    gender:     GenderEnum
    birth_date: date
    phone:      Optional[str] = None
    address:    Optional[str] = None
    city:       Optional[str] = None
    country:    Optional[str] = "Bolivia"
    photo_url:  Optional[str] = None


class PersonUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name:  Optional[str] = None
    ci:         Optional[str] = None
    gender:     Optional[GenderEnum] = None
    birth_date: Optional[date] = None
    phone:      Optional[str] = None
    address:    Optional[str] = None
    city:       Optional[str] = None
    country:    Optional[str] = None
    photo_url:  Optional[str] = None


class PersonOut(BaseModel):
    id:         int
    user_id:    Optional[int] = None
    first_name: str
    last_name:  str
    ci:         str
    gender:     GenderEnum
    birth_date: date
    phone:      Optional[str]
    address:    Optional[str]
    city:       Optional[str]
    country:    Optional[str]
    photo_url:  Optional[str]
    created_at: datetime
    age:        int = 0   # campo calculado, no viene de la DB

    model_config = {"from_attributes": True}

    @field_validator("age", mode="before")
    @classmethod
    def calculate_age(cls, v, info):
        # Calculamos la edad a partir de birth_date en los datos del modelo
        birth_date = info.data.get("birth_date")
        if not birth_date:
            return 0
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def model_post_init(self, __context) -> None:
        # Recalculamos age después de que Pydantic construye el objeto
        today = date.today()
        self.age = today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
