from decimal import Decimal
from pydantic import BaseModel


class InformacionCargaCreate(BaseModel):
    tipo:         str
    cantidad:     Decimal
    peso_item:    Decimal
    volumen_item: Decimal


class InformacionCargaUpdate(BaseModel):
    tipo:         str | None = None
    cantidad:     Decimal | None = None
    peso_item:    Decimal | None = None
    volumen_item: Decimal | None = None


class InformacionCargaOut(BaseModel):
    id:                  int
    tipo:                str
    cantidad:            Decimal
    peso_item:           Decimal
    volumen_item:        Decimal
    peso:                Decimal
    volumen:             Decimal
    id_servicio_cliente: int

    model_config = {"from_attributes": True}