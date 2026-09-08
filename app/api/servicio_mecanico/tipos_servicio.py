from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.tipo_servicio import TipoServicioCreate, TipoServicioUpdate, TipoServicioOut
from app.services.tipo_servicio_service import TipoServicioService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> TipoServicioService:
    return TipoServicioService(db)


@router.get("/", response_model=list[TipoServicioOut])
def list_tipos(
    skip: int = 0, limit: int = 100,
    svc: TipoServicioService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=TipoServicioOut, status_code=status.HTTP_201_CREATED)
def create_tipo(
    data: TipoServicioCreate,
    svc: TipoServicioService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{tipo_id}", response_model=TipoServicioOut)
def get_tipo(
    tipo_id: int,
    svc: TipoServicioService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(tipo_id)


@router.patch("/{tipo_id}", response_model=TipoServicioOut)
def update_tipo(
    tipo_id: int, data: TipoServicioUpdate,
    svc: TipoServicioService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(tipo_id, data)


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo(
    tipo_id: int,
    svc: TipoServicioService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(tipo_id)

@router.patch("/{tipo_id}/toggle", response_model=TipoServicioOut)
def toggle_active(
    tipo_id: int,
    svc: TipoServicioService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(tipo_id)