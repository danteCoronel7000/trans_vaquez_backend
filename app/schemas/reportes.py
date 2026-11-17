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

class FilaServicioCliente(BaseModel):
    id_servicio:                 int
    fecha:                       datetime
    origen:                      str
    destino:                     str
    camion:                      str
    chofer:                      str
    estado:                      str
    peso_carga:                  float
    volumen_carga:               float
    costo_cliente:               float
    # Campos calculados
    costo_por_kg:                float | None
    costo_por_m3:                float | None
    ocupacion_peso_pct:          float | None
    ocupacion_volumen_pct:       float | None
    participacion_pct:           float
    costo_operativo_prorrateado: float
    utilidad_estimada:           float


class ResumenCliente(BaseModel):
    total_servicios:       int
    servicios_cancelados:  int
    peso_total:            float
    volumen_total:         float
    costo_total:           float
    costo_operativo_total: float
    utilidad_total:        float
    costo_promedio_por_kg: float | None


class GrupoCliente(BaseModel):
    id_cliente:   int
    cliente:      str
    razon_social: str | None
    nit:          str | None
    filas:        list[FilaServicioCliente]
    resumen:      ResumenCliente


class ReporteServiciosPorClienteResponse(BaseModel):
    filtro_aplicado: FiltroReporteServicios
    total_clientes:  int
    grupos:          list[GrupoCliente]
    resumen_general: ResumenCliente

class FilaViajeChofer(BaseModel):
    id_servicio:                 int
    fecha:                       datetime
    ruta:                        str
    origen:                      str
    destino:                     str
    camion:                      str
    estado:                      str
    num_clientes:                int
    distancia_km:                float | None
    tiempo_estimado_h:           float | None
    viaticos_chofer:             float
    # Campos calculados
    peso_transportado:           float
    volumen_transportado:        float
    ingresos_viaje:              float
    costo_operativo:             float
    utilidad_viaje:              float
    ocupacion_peso_pct:          float | None
    costo_operativo_por_km:      float | None
    velocidad_promedio_estimada: float | None
    duracion_real_horas:         float | None


class ResumenChofer(BaseModel):
    total_viajes:          int      # programados + en curso + finalizados
    viajes_programados:    int
    viajes_en_curso:       int
    viajes_finalizados:    int
    viajes_cancelados:     int
    km_total:              float
    horas_estimadas_total: float
    peso_total:            float
    volumen_total:         float
    ingresos_total:        float
    costo_operativo_total: float
    viaticos_chofer_total: float
    utilidad_total:        float


class GrupoChofer(BaseModel):
    id_chofer: int
    chofer:    str
    licencia:  str | None
    categoria: str | None
    filas:     list[FilaViajeChofer]
    resumen:   ResumenChofer


class ReporteViajesPorChoferResponse(BaseModel):
    filtro_aplicado: FiltroReporteServicios
    total_choferes:  int
    grupos:          list[GrupoChofer]
    resumen_general: ResumenChofer