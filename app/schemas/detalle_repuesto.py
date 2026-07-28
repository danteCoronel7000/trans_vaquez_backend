from decimal import Decimal
from pydantic import BaseModel
from app.schemas.repuesto import RepuestoOut


class DetalleCreate(BaseModel):
    repuesto_id:     int
    cantidad:        Decimal
    precio_unitario: Decimal


class DetalleUpdate(BaseModel):
    cantidad:        Decimal | None = None
    precio_unitario: Decimal | None = None


class DetalleOut(BaseModel):
    id:              int
    mantenimiento_id: int
    repuesto_id:     int
    cantidad:        Decimal
    precio_unitario: Decimal
    subtotal:        Decimal
    repuesto:        RepuestoOut

    model_config = {"from_attributes": True}