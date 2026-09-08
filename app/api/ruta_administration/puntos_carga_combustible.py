from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.punto_carga_combustible import PuntoCargaCreate, PuntoCargaUpdate, PuntoCargaOut
from app.services.punto_carga_combustible_service import PuntoCargaCombustibleService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> PuntoCargaCombustibleService:
    return PuntoCargaCombustibleService(db)


@router.get("/", response_model=list[PuntoCargaOut])
def list_puntos(
    skip: int = 0, limit: int = 100,
    svc: PuntoCargaCombustibleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=PuntoCargaOut, status_code=status.HTTP_201_CREATED)
def create_punto(
    data: PuntoCargaCreate,
    svc: PuntoCargaCombustibleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{punto_id}", response_model=PuntoCargaOut)
def get_punto(
    punto_id: int,
    svc: PuntoCargaCombustibleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(punto_id)


@router.patch("/{punto_id}", response_model=PuntoCargaOut)
def update_punto(
    punto_id: int, data: PuntoCargaUpdate,
    svc: PuntoCargaCombustibleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(punto_id, data)

@router.patch("/{punto_id}/toggle", response_model=PuntoCargaOut)
def toggle_active(
    punto_id: int,
    svc: PuntoCargaCombustibleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(punto_id)

@router.delete("/{punto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_punto(
    punto_id: int,
    svc: PuntoCargaCombustibleService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(punto_id)