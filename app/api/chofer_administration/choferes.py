from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.chofer import ChoferCreate, ChoferUpdate, ChoferOut, ChoferDetailOut
from app.services.chofer_service import ChoferService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ChoferService:
    return ChoferService(db)


@router.get("/", response_model=list[ChoferDetailOut])
def list_choferes(
    skip: int = 0,
    limit: int = 100,
    svc: ChoferService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=ChoferOut, status_code=status.HTTP_201_CREATED)
def create_chofer(
    data: ChoferCreate,
    svc: ChoferService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{chofer_id}", response_model=ChoferDetailOut)
def get_chofer(
    chofer_id: int,
    svc: ChoferService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(chofer_id)


@router.patch("/{chofer_id}", response_model=ChoferOut)
def update_chofer(
    chofer_id: int,
    data: ChoferUpdate,
    svc: ChoferService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(chofer_id, data)


@router.delete("/{chofer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chofer(
    chofer_id: int,
    svc: ChoferService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(chofer_id)


@router.patch("/{chofer_id}/toggle", response_model=ChoferOut)
def toggle_active(
    chofer_id: int,
    svc: ChoferService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(chofer_id)