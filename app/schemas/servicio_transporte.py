from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel
from app.models.servicio_transporte import EstadoServicioEnum
from app.schemas.servicio_cliente import ServicioClienteOut, ServicioClienteCreate
from app.schemas.ruta import RutaOut
from app.schemas.chofer import ChoferDetailOut
from app.schemas.camion import CamionOut
from app.schemas.servicio_cliente import PersonaContactoOut, InformacionCargaOut
from app.schemas.ruta import RutaOut  # ajusta el import si el nombre real es distinto


class ServicioTransporteCreate(BaseModel):
    punto_carga:       str
    punto_descarga:    str
    viaticos_chofer:   Decimal | None = 0
    viaticos_ayudante: Decimal | None = 0
    combustible:       Decimal | None = 0
    id_ruta:           int
    id_usuario_sistema: int
    id_chofer:         int
    id_camion:         int
    servicios_cliente:  list[ServicioClienteCreate] = []

class ServicioTransporteUpdate(BaseModel):
    punto_carga:       str | None = None
    punto_descarga:    str | None = None
    viaticos_chofer:   Decimal | None = None
    viaticos_ayudante: Decimal | None = None
    combustible:       Decimal | None = None
    id_ruta:           int | None = None
    id_usuario_sistema: int | None = None
    id_chofer:         int | None = None
    id_camion:         int | None = None


class ServicioTransporteOut(BaseModel):
    id:                  int
    punto_carga:         str
    punto_descarga:      str
    viaticos_chofer:     Decimal | None
    viaticos_ayudante:   Decimal | None
    combustible:         Decimal | None
    estado:              EstadoServicioEnum
    id_ruta:             int
    id_usuario_sistema:  int
    id_chofer:           int
    id_camion:           int
    fecha_creacion:      datetime
    fecha_actualizacion: datetime | None
    motivo_cancelacion: str | None = None
    servicios_cliente:   list[ServicioClienteOut] = []
    ruta:                RutaOut
    chofer:              ChoferDetailOut
    camion:              CamionOut
    model_config = {"from_attributes": True}

class CancelarServicioRequest(BaseModel):
    motivo: str

class ChoferResumenOut(BaseModel):
    person: PersonaContactoOut
    model_config = {"from_attributes": True}


class CamionResumenOut(BaseModel):
    placa: str
    marca: str
    modelo: str
    model_config = {"from_attributes": True}


class MiCargaOut(BaseModel):
    id: int
    peso_total: Decimal
    volumen_total: Decimal
    costo_total: Decimal
    informaciones_carga: list[InformacionCargaOut] = []
    model_config = {"from_attributes": True}


class ServicioTransporteClienteOut(BaseModel):
    id: int
    estado: EstadoServicioEnum
    punto_carga: str
    punto_descarga: str
    fecha_creacion: datetime
    motivo_cancelacion: str | None = None
    ruta: RutaOut
    chofer: ChoferResumenOut
    camion: CamionResumenOut
    mi_carga: MiCargaOut

    model_config = {"from_attributes": True}