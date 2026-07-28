from pydantic import BaseModel


class TallerCreate(BaseModel):
    nombre:      str
    telefono:    str | None = None
    direccion:   str | None = None
    ciudad:      str | None = None
    contacto:    str | None = None
    observacion: str | None = None


class TallerUpdate(BaseModel):
    nombre:      str | None = None
    telefono:    str | None = None
    direccion:   str | None = None
    ciudad:      str | None = None
    contacto:    str | None = None
    observacion: str | None = None
    is_active: bool  # 👈 se muestra siempre en la respuesta


class TallerOut(BaseModel):
    id:          int
    nombre:      str
    telefono:    str | None
    direccion:   str | None
    ciudad:      str | None
    contacto:    str | None
    observacion: str | None
    is_active: bool  # 👈 se muestra siempre en la respuesta

    model_config = {"from_attributes": True}