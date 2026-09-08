from decimal import Decimal
from pydantic import BaseModel
from app.schemas.informacion_carga import InformacionCargaOut, InformacionCargaCreate


class ServicioClienteCreate(BaseModel):
    id_cliente:          int
    costo_total:         Decimal
    informaciones_carga: list[InformacionCargaCreate] = []


class ServicioClienteUpdate(BaseModel):
    costo_total: Decimal | None = None


class PersonaContactoOut(BaseModel):
    first_name: str
    last_name: str
    phone: str | None = None

    model_config = {"from_attributes": True}


class ClienteResumenOut(BaseModel):
    id: int
    razon_social: str | None = None
    person: PersonaContactoOut

    model_config = {"from_attributes": True}

class ServicioClienteOut(BaseModel):
    id:                     int
    id_servicio_transporte: int
    id_cliente:             int
    peso_total:             Decimal
    volumen_total:          Decimal
    costo_total:            Decimal
    cliente:                ClienteResumenOut
    informaciones_carga:    list[InformacionCargaOut] = []

    model_config = {"from_attributes": True}