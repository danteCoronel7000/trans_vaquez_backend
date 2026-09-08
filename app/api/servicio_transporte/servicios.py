from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.schemas.servicio_transporte import ServicioTransporteClienteOut, ServicioTransporteCreate, ServicioTransporteUpdate, ServicioTransporteOut
from app.schemas.servicio_cliente import ServicioClienteCreate, ServicioClienteUpdate
from app.schemas.informacion_carga import InformacionCargaCreate, InformacionCargaUpdate
from app.services.servicio_transporte_service import ServicioTransporteService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.servicio_transporte import CancelarServicioRequest
from app.models.user import User

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ServicioTransporteService:
    return ServicioTransporteService(db)


# ── CRUD principal ─────────────────────────────────────────
@router.get("/mi-servicio-activo", response_model=ServicioTransporteOut)
def get_mi_servicio_activo(
    svc: ServicioTransporteService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.get_activo_por_usuario(current_user)

@router.get("/", response_model=list[ServicioTransporteOut])
def list_servicios(
    skip: int = 0, limit: int = 100,
    q: str | None = Query(None, description="Buscar por punto de carga o descarga"),
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    if q:
        return svc.search(q, skip, limit)
    return svc.get_all(skip, limit)


@router.post("/", response_model=ServicioTransporteOut, status_code=status.HTTP_201_CREATED)
def create_servicio(
    data: ServicioTransporteCreate,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)

@router.get("/mis-servicios", response_model=list[ServicioTransporteClienteOut])
def get_mis_servicios(
    svc: ServicioTransporteService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.get_mis_servicios(current_user)

@router.get("/{servicio_id}", response_model=ServicioTransporteOut)
def get_servicio(
    servicio_id: int,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(servicio_id)


@router.patch("/{servicio_id}", response_model=ServicioTransporteOut)
def update_servicio(
    servicio_id: int, data: ServicioTransporteUpdate,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(servicio_id, data)


# ── Transiciones de estado ────────────────────────────────
@router.patch("/{servicio_id}/iniciar", response_model=ServicioTransporteOut)
def iniciar_servicio(
    servicio_id: int,
    svc: ServicioTransporteService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.iniciar(servicio_id, current_user)


@router.patch("/{servicio_id}/finalizar", response_model=ServicioTransporteOut)
def finalizar_servicio(
    servicio_id: int,
    svc: ServicioTransporteService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.finalizar(servicio_id, current_user)


@router.patch("/{servicio_id}/cancelar", response_model=ServicioTransporteOut)
def cancelar_servicio(
    servicio_id: int,
    data: CancelarServicioRequest,
    svc: ServicioTransporteService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.cancelar(servicio_id, data.motivo, current_user)
# ── Gestión de clientes ───────────────────────────────────
@router.post("/{servicio_id}/clientes", response_model=ServicioTransporteOut)
def add_cliente(
    servicio_id: int, data: ServicioClienteCreate,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.add_cliente(servicio_id, data)


@router.patch("/{servicio_id}/clientes/{sc_id}", response_model=ServicioTransporteOut)
def update_cliente(
    servicio_id: int, sc_id: int, data: ServicioClienteUpdate,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update_cliente(servicio_id, sc_id, data)


@router.delete("/{servicio_id}/clientes/{sc_id}", response_model=ServicioTransporteOut)
def remove_cliente(
    servicio_id: int, sc_id: int,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.remove_cliente(servicio_id, sc_id)


# ── Gestión de información de carga ───────────────────────
@router.post("/{servicio_id}/clientes/{sc_id}/carga", response_model=ServicioTransporteOut)
def add_carga(
    servicio_id: int, sc_id: int, data: InformacionCargaCreate,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.add_carga(servicio_id, sc_id, data)


@router.patch("/{servicio_id}/clientes/{sc_id}/carga/{carga_id}", response_model=ServicioTransporteOut)
def update_carga(
    servicio_id: int, sc_id: int, carga_id: int, data: InformacionCargaUpdate,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update_carga(servicio_id, sc_id, carga_id, data)


@router.delete("/{servicio_id}/clientes/{sc_id}/carga/{carga_id}", response_model=ServicioTransporteOut)
def remove_carga(
    servicio_id: int, sc_id: int, carga_id: int,
    svc: ServicioTransporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.remove_carga(servicio_id, sc_id, carga_id)