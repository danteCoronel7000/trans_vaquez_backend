from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel
from app.schemas.taller_mecanico import TallerOut
from app.schemas.tipo_servicio import TipoServicioOut
from app.schemas.detalle_repuesto import DetalleOut


class ServicioCreate(BaseModel):
    camion_id:        int
    taller_id:        int
    tipo_servicio_id: int
    fecha:            date
    kilometraje:      int | None = None
    descripcion:      str | None = None
    mano_obra:        Decimal
    observaciones:    str | None = None


class ServicioUpdate(BaseModel):
    taller_id:        int | None = None
    tipo_servicio_id: int | None = None
    fecha:            date | None = None
    kilometraje:      int | None = None
    descripcion:      str | None = None
    mano_obra:        Decimal | None = None
    observaciones:    str | None = None


class ServicioOut(BaseModel):
    id:                 int
    camion_id:          int
    taller_id:          int
    tipo_servicio_id:   int
    fecha:              date
    kilometraje:        int | None
    descripcion:        str | None
    mano_obra:          Decimal
    subtotal_repuestos: Decimal
    total:              Decimal
    observaciones:      str | None
    created_at:         datetime
    taller:             TallerOut
    tipo_servicio:      TipoServicioOut
    detalles:           list[DetalleOut] = []

    model_config = {"from_attributes": True}