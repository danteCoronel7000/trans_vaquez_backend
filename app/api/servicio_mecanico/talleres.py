from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.taller_mecanico import TallerCreate, TallerUpdate, TallerOut
from app.services.taller_mecanico_service import TallerMecanicoService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> TallerMecanicoService:
    return TallerMecanicoService(db)


@router.get("/", response_model=list[TallerOut])
def list_talleres(
    skip: int = 0, limit: int = 100,
    svc: TallerMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=TallerOut, status_code=status.HTTP_201_CREATED)
def create_taller(
    data: TallerCreate,
    svc: TallerMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{taller_id}", response_model=TallerOut)
def get_taller(
    taller_id: int,
    svc: TallerMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(taller_id)


@router.patch("/{taller_id}", response_model=TallerOut)
def update_taller(
    taller_id: int, data: TallerUpdate,
    svc: TallerMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(taller_id, data)


@router.delete("/{taller_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_taller(
    taller_id: int,
    svc: TallerMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(taller_id)

@router.patch("/{taller_id}/toggle", response_model=TallerOut)
def toggle_active(
    taller_id: int,
    svc: TallerMecanicoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(taller_id)