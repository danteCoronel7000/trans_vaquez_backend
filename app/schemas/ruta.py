from pydantic import BaseModel
from app.schemas.punto_peaje import PuntoPeajeOut
from app.schemas.punto_carga_combustible import PuntoCargaOut


class RutaCreate(BaseModel):
    nombre:          str
    ciudad_origen:   str
    ciudad_destino:  str
    distancia:       float | None = None
    tiempo_estimado: float | None = None
    tipo_de_via:     str | None = None


class RutaUpdate(BaseModel):
    nombre:          str | None = None
    ciudad_origen:   str | None = None
    ciudad_destino:  str | None = None
    distancia:       float | None = None
    tiempo_estimado: float | None = None
    tipo_de_via:     str | None = None
    is_active:       bool | None = None


class RutaOut(BaseModel):
    id:              int
    nombre:          str
    ciudad_origen:   str
    ciudad_destino:  str
    distancia:       float | None
    tiempo_estimado: float | None
    tipo_de_via:     str | None
    is_active:       bool
    peajes:          list[PuntoPeajeOut] = []
    puntos_carga:    list[PuntoCargaOut] = []

    model_config = {"from_attributes": True}