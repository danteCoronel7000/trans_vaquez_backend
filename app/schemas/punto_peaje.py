from pydantic import BaseModel


class PuntoPeajeCreate(BaseModel):
    nombre:       str
    departamento: str | None = None


class PuntoPeajeUpdate(BaseModel):
    nombre:       str | None = None
    departamento: str | None = None


class PuntoPeajeOut(BaseModel):
    id:           int
    nombre:       str
    departamento: str | None
    is_active:    bool

    model_config = {"from_attributes": True}