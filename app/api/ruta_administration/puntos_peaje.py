from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.punto_peaje import PuntoPeajeCreate, PuntoPeajeUpdate, PuntoPeajeOut
from app.services.punto_peaje_service import PuntoPeajeService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> PuntoPeajeService:
    return PuntoPeajeService(db)


@router.get("/", response_model=list[PuntoPeajeOut])
def list_puntos(
    skip: int = 0, limit: int = 100,
    svc: PuntoPeajeService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=PuntoPeajeOut, status_code=status.HTTP_201_CREATED)
def create_punto(
    data: PuntoPeajeCreate,
    svc: PuntoPeajeService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{punto_id}", response_model=PuntoPeajeOut)
def get_punto(
    punto_id: int,
    svc: PuntoPeajeService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(punto_id)


@router.patch("/{punto_id}", response_model=PuntoPeajeOut)
def update_punto(
    punto_id: int, data: PuntoPeajeUpdate,
    svc: PuntoPeajeService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(punto_id, data)


@router.delete("/{punto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_punto(
    punto_id: int,
    svc: PuntoPeajeService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(punto_id)