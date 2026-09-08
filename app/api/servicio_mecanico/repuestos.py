from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.repuesto import RepuestoCreate, RepuestoUpdate, RepuestoOut
from app.services.repuesto_service import RepuestoService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> RepuestoService:
    return RepuestoService(db)


@router.get("/", response_model=list[RepuestoOut])
def list_repuestos(
    skip: int = 0, limit: int = 100,
    svc: RepuestoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=RepuestoOut, status_code=status.HTTP_201_CREATED)
def create_repuesto(
    data: RepuestoCreate,
    svc: RepuestoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{repuesto_id}", response_model=RepuestoOut)
def get_repuesto(
    repuesto_id: int,
    svc: RepuestoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(repuesto_id)


@router.patch("/{repuesto_id}", response_model=RepuestoOut)
def update_repuesto(
    repuesto_id: int, data: RepuestoUpdate,
    svc: RepuestoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(repuesto_id, data)


@router.delete("/{repuesto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repuesto(
    repuesto_id: int,
    svc: RepuestoService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(repuesto_id)

@router.patch("/{repuesto_id}/toggle", response_model=RepuestoOut)
def toggle_active(
    repuesto_id: int,
    svc: RepuestoService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(repuesto_id)