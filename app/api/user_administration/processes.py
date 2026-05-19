from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.process import ProcessCreate, ProcessUpdate, ProcessOut
from app.services.process_service import ProcessService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ProcessService:
    return ProcessService(db)


@router.get("/", response_model=list[ProcessOut])
def list_processes(
    skip: int = 0,
    limit: int = 100,
    svc: ProcessService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=ProcessOut, status_code=status.HTTP_201_CREATED)
def create_process(
    data: ProcessCreate,
    svc: ProcessService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{process_id}", response_model=ProcessOut)
def get_process(
    process_id: int,
    svc: ProcessService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(process_id)


@router.patch("/{process_id}", response_model=ProcessOut)
def update_process(
    process_id: int,
    data: ProcessUpdate,
    svc: ProcessService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(process_id, data)


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_process(
    process_id: int,
    svc: ProcessService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(process_id)