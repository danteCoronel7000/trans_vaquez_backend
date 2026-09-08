from pydantic import BaseModel


class TipoServicioCreate(BaseModel):
    nombre:      str
    descripcion: str | None = None


class TipoServicioUpdate(BaseModel):
    nombre:      str | None = None
    descripcion: str | None = None
    is_active: bool | None = None

class TipoServicioOut(BaseModel):
    id:          int
    nombre:      str
    descripcion: str | None
    is_active: bool | None = None

    model_config = {"from_attributes": True}