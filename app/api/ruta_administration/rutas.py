from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.ruta import RutaCreate, RutaUpdate, RutaOut
from app.services.ruta_service import RutaService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> RutaService:
    return RutaService(db)


@router.get("/", response_model=list[RutaOut])
def list_rutas(
    skip: int = 0, limit: int = 100,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=RutaOut, status_code=status.HTTP_201_CREATED)
def create_ruta(
    data: RutaCreate,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{ruta_id}", response_model=RutaOut)
def get_ruta(
    ruta_id: int,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(ruta_id)


@router.patch("/{ruta_id}", response_model=RutaOut)
def update_ruta(
    ruta_id: int, data: RutaUpdate,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(ruta_id, data)


@router.delete("/{ruta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ruta(
    ruta_id: int,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(ruta_id)


@router.patch("/{ruta_id}/toggle", response_model=RutaOut)
def toggle_active(
    ruta_id: int,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(ruta_id)


# Peajes
@router.post("/{ruta_id}/peajes/{peaje_id}", response_model=RutaOut)
def assign_peaje(
    ruta_id: int, peaje_id: int,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.assign_peaje(ruta_id, peaje_id)


@router.delete("/{ruta_id}/peajes/{peaje_id}", response_model=RutaOut)
def remove_peaje(
    ruta_id: int, peaje_id: int,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.remove_peaje(ruta_id, peaje_id)


# Puntos de carga
@router.post("/{ruta_id}/puntos-carga/{punto_id}", response_model=RutaOut)
def assign_punto_carga(
    ruta_id: int, punto_id: int,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.assign_punto_carga(ruta_id, punto_id)


@router.delete("/{ruta_id}/puntos-carga/{punto_id}", response_model=RutaOut)
def remove_punto_carga(
    ruta_id: int, punto_id: int,
    svc: RutaService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.remove_punto_carga(ruta_id, punto_id)