from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.servicio_mecanico import ServicioCreate, ServicioUpdate, ServicioOut
from app.schemas.detalle_repuesto import DetalleCreate, DetalleUpdate, DetalleOut
from app.services.servicio_mecanico_service import ServicioMecanicoService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ServicioMecanicoService:
    return ServicioMecanicoService(db)


@router.get("/", response_model=list[ServicioOut])
def list_servicios(
    skip: int = 0, limit: int = 100,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.get("/camion/{camion_id}", response_model=list[ServicioOut])
def list_servicios_by_camion(
    camion_id: int,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_camion(camion_id)


@router.post("/", response_model=ServicioOut, status_code=status.HTTP_201_CREATED)
def create_servicio(
    data: ServicioCreate,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{servicio_id}", response_model=ServicioOut)
def get_servicio(
    servicio_id: int,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(servicio_id)


@router.patch("/{servicio_id}", response_model=ServicioOut)
def update_servicio(
    servicio_id: int, data: ServicioUpdate,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(servicio_id, data)


@router.delete("/{servicio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_servicio(
    servicio_id: int,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(servicio_id)


# Detalle repuestos
@router.post("/{servicio_id}/detalles", response_model=ServicioOut)
def add_detalle(
    servicio_id: int, data: DetalleCreate,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.add_detalle(servicio_id, data)


@router.patch("/{servicio_id}/detalles/{detalle_id}", response_model=ServicioOut)
def update_detalle(
    servicio_id: int, detalle_id: int, data: DetalleUpdate,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update_detalle(servicio_id, detalle_id, data)


@router.delete("/{servicio_id}/detalles/{detalle_id}", response_model=ServicioOut)
def remove_detalle(
    servicio_id: int, detalle_id: int,
    svc: ServicioMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.remove_detalle(servicio_id, detalle_id)