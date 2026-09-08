from datetime import datetime
from pydantic import BaseModel


class UbicacionGPSCreate(BaseModel):
    latitud:   float
    longitud:  float
    velocidad: float | None = None


class UbicacionGPSOut(BaseModel):
    id:         int
    latitud:    float
    longitud:   float
    velocidad:  float | None
    fecha_hora: datetime

    model_config = {"from_attributes": True}