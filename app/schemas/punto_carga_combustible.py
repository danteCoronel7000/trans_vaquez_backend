from pydantic import BaseModel


class PuntoCargaCreate(BaseModel):
    nombre:       str
    direccion:    str | None = None
    ciudad:       str | None = None
    departamento: str | None = None


class PuntoCargaUpdate(BaseModel):
    nombre:       str | None = None
    direccion:    str | None = None
    ciudad:       str | None = None
    departamento: str | None = None
    is_active:    bool | None = None 


class PuntoCargaOut(BaseModel):
    id:           int
    nombre:       str
    direccion:    str | None
    ciudad:       str | None
    departamento: str | None
    is_active:    bool

    model_config = {"from_attributes": True}