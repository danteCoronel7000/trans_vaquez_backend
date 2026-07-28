from pydantic import BaseModel
from datetime import date, datetime


class CamionCreate(BaseModel):
    placa:                         str
    marca:                         str
    modelo:                        str
    color:                         str
    capacidad_carga_kg:            float
    volumen_capacity_m3:           float
    anio:                          int
    numero_chasis:                 str
    numero_motor:                  str
    vencimiento_soat:              date
    vencimiento_inspeccion_tecnica: date


class CamionUpdate(BaseModel):
    placa:                         str | None = None
    marca:                         str | None = None
    modelo:                        str | None = None
    color:                         str | None = None
    capacidad_carga_kg:            float | None = None
    volumen_capacity_m3:           float | None = None
    anio:                          int | None = None
    numero_chasis:                 str | None = None
    numero_motor:                  str | None = None
    vencimiento_soat:              date | None = None
    vencimiento_inspeccion_tecnica: date | None = None
    is_active:                     bool | None = None


class ImageOut(BaseModel):
    id:        int
    name:      str | None
    image_url: str | None
    image_id:  str | None

    model_config = {"from_attributes": True}


class CamionOut(BaseModel):
    id:                            int
    placa:                         str
    marca:                         str
    modelo:                        str
    color:                         str
    capacidad_carga_kg:            float
    volumen_capacity_m3:           float
    anio:                          int
    numero_chasis:                 str
    numero_motor:                  str
    vencimiento_soat:              date
    vencimiento_inspeccion_tecnica: date
    is_active:                     bool
    created_at:                    datetime
    image:                         ImageOut | None = None

    model_config = {"from_attributes": True}