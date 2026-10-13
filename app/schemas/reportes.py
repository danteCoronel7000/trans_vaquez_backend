from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel


class FiltroReporteServicios(BaseModel):
    tipo_periodo: str          # "fecha_especifica" | "rango" | "todos"
    fecha_inicio: date | None = None
    fecha_fin:    date | None = None


class UbicacionGPSResumen(BaseModel):
    latitud:    float
    longitud:   float
    fecha_hora: datetime


class FilaReporteServicio(BaseModel):
    id_servicio:        int
    cliente:             str
    origen:               str
    destino:              str
    camion:               str
    chofer:               str
    fecha:                datetime
    estado:                str
    peso_carga:            Decimal
    volumen_carga:         Decimal
    costo_cliente:         Decimal
    distancia_ruta:        float | None
    tiempo_estimado_ruta:  float | None
    ultima_ubicacion:      UbicacionGPSResumen | None
    num_clientes_servicio: int


class ReporteServiciosResponse(BaseModel):
    filtro_aplicado: FiltroReporteServicios
    total_filas:     int
    filas:           list[FilaReporteServicio]