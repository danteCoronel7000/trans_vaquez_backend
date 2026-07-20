from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.client import ClientCreate, ClientUpdate, ClientOut, ClientDetailOut
from app.services.client_service import ClientService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ClientService:
    return ClientService(db)


@router.get("/", response_model=list[ClientDetailOut])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    svc: ClientService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    svc: ClientService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{client_id}", response_model=ClientDetailOut)
def get_client(
    client_id: int,
    svc: ClientService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(client_id)


@router.patch("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    data: ClientUpdate,
    svc: ClientService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(client_id, data)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    svc: ClientService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(client_id)


@router.patch("/{client_id}/toggle", response_model=ClientOut)
def toggle_active(
    client_id: int,
    svc: ClientService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(client_id)