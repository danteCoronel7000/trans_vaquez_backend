from pydantic import BaseModel


class RepuestoCreate(BaseModel):
    nombre:      str
    marca:       str | None = None
    unidad:      str
    descripcion: str | None = None


class RepuestoUpdate(BaseModel):
    nombre:      str | None = None
    marca:       str | None = None
    unidad:      str | None = None
    descripcion: str | None = None


class RepuestoOut(BaseModel):
    id:          int
    nombre:      str
    marca:       str | None
    unidad:      str
    descripcion: str | None

    model_config = {"from_attributes": True}