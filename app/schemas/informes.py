from datetime import date, datetime
from pydantic import BaseModel

from pydantic import BaseModel, Field


class FiltroInformeMensual(BaseModel):
    anio: int = Field(ge=2000, le=2100)
    mes:  int = Field(ge=1, le=12)

class FiltroInformeSemanal(BaseModel):
    fecha_referencia: date      # cualquier día de la semana a consultar


class Periodo(BaseModel):
    inicio: date
    fin:    date


# ── 2. Resumen ejecutivo ──────────────────────────────────
class ResumenEjecutivo(BaseModel):
    total_servicios:      int
    programados:          int
    en_curso:             int
    finalizados:          int
    cancelados:           int
    tasa_cancelacion_pct: float | None
    peso_total_kg:        float
    volumen_total_m3:     float
    ingresos:             float
    costo_operativo:      float
    costo_mantenimiento:  float
    utilidad_bruta:       float
    utilidad_neta:        float
    margen_pct:           float | None


# ── 3. Comparativo ────────────────────────────────────────
class IndicadorComparado(BaseModel):
    nombre:         str
    unidad:         str
    actual:         float
    anterior:       float
    variacion_pct:  float | None
    mejor_si_sube:  bool        # para colorear: en costos, subir es malo


# ── 4. Costos ─────────────────────────────────────────────
class ItemCosto(BaseModel):
    concepto:   str
    monto:      float
    porcentaje: float | None


class DesgloseCostos(BaseModel):
    items:         list[ItemCosto]
    total_costos:  float
    ingresos:      float
    utilidad_neta: float


# ── 5. Actividad diaria ───────────────────────────────────
class ActividadDia(BaseModel):
    fecha:      date
    dia_semana: str
    servicios:  int
    cancelados: int
    peso_kg:    float
    ingresos:   float


# ── 6. Detalle de servicios ───────────────────────────────
class DetalleServicio(BaseModel):
    id_servicio:     int
    fecha:           datetime
    ruta:            str
    clientes:        str
    camion:          str
    chofer:          str
    estado:          str
    peso_kg:         float
    volumen_m3:      float
    ingresos:        float
    costo_operativo: float


# ── 7. Flota ──────────────────────────────────────────────
class FilaFlota(BaseModel):
    id_camion:              int
    camion:                 str
    viajes:                 int
    km:                     float
    peso_kg:                float
    ocupacion_promedio_pct: float | None
    mantenimientos:         int
    costo_mantenimiento:    float
    sin_actividad:          bool


class ResumenFlota(BaseModel):
    camiones_activos:       int
    camiones_con_actividad: int
    camiones_sin_actividad: int
    utilizacion_pct:        float | None
    filas:                  list[FilaFlota]


# ── 8. Rutas y destinos ───────────────────────────────────
class FilaRutaDestino(BaseModel):
    nombre:    str
    detalle:   str | None
    servicios: int
    peso_kg:   float
    ingresos:  float


class RutasDestinos(BaseModel):
    por_ruta:    list[FilaRutaDestino]
    por_destino: list[FilaRutaDestino]


# ── 9. Incidencias ────────────────────────────────────────
class ServicioBasico(BaseModel):
    id_servicio: int
    fecha:       datetime
    ruta:        str
    camion:      str
    chofer:      str


class IncidenciaCancelado(ServicioBasico):
    motivo: str | None


class Incidencias(BaseModel):
    cancelados: list[IncidenciaCancelado]
    en_curso:   list[ServicioBasico]


# ── 10. Alertas de cumplimiento ───────────────────────────
class AlertaDocumento(BaseModel):
    camion:            str
    documento:         str
    fecha_vencimiento: date
    dias_restantes:    int
    nivel:             str      # "vencido" | "por_vencer"


# ── 11. Top clientes ──────────────────────────────────────
class TopCliente(BaseModel):
    cliente:   str
    servicios: int
    peso_kg:   float
    ingresos:  float


# ── 12. Productividad por chofer ──────────────────────────
class ProductividadChofer(BaseModel):
    chofer:          str
    viajes:          int
    km:              float
    horas_estimadas: float
    peso_kg:         float
    viaticos:        float


# ── 13. Agenda del próximo período ────────────────────────
class AgendaServicio(BaseModel):
    id_servicio:  int
    fecha_salida: datetime
    ruta:         str
    clientes:     str
    camion:       str
    chofer:       str


class AgendaProxima(BaseModel):
    inicio:                date
    fin:                   date
    servicios:             list[AgendaServicio]
    programados_sin_fecha: int


# ── 14. Distancia real por GPS ────────────────────────────
class FilaDistanciaGPS(BaseModel):
    id_servicio:     int
    ruta:            str
    camion:          str
    km_planificados: float | None
    km_gps:          float
    diferencia_pct:  float | None


class DistanciaGPS(BaseModel):
    servicios_con_gps: int
    km_gps_total:      float
    filas:             list[FilaDistanciaGPS]


# ── Respuesta completa ────────────────────────────────────
class InformeResponse(BaseModel):
    tipo:             str            # "semanal" | "mensual"
    periodo:          Periodo
    periodo_anterior: Periodo
    emitido_por:      str
    emitido_en:       datetime
    resumen:          ResumenEjecutivo
    comparativo:      list[IndicadorComparado]
    costos:           DesgloseCostos
    actividad_diaria: list[ActividadDia]
    servicios:        list[DetalleServicio]
    flota:            ResumenFlota
    rutas_destinos:   RutasDestinos
    incidencias:      Incidencias
    alertas:          list[AlertaDocumento]
    top_clientes:     list[TopCliente]
    choferes:         list[ProductividadChofer]
    agenda:           AgendaProxima
    distancia_gps:    DistanciaGPS