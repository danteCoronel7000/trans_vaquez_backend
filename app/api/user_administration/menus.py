from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.menu import MenuCreate, MenuUpdate, MenuOut
from app.schemas.process import ProcessOut
from app.services.menu_service import MenuService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> MenuService:
    return MenuService(db)


@router.get("/", response_model=list[MenuOut])
def list_menus(
    skip: int = 0,
    limit: int = 100,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=MenuOut, status_code=status.HTTP_201_CREATED)
def create_menu(
    data: MenuCreate,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{menu_id}", response_model=MenuOut)
def get_menu(
    menu_id: int,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(menu_id)


@router.patch("/{menu_id}", response_model=MenuOut)
def update_menu(
    menu_id: int,
    data: MenuUpdate,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(menu_id, data)


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu(
    menu_id: int,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(menu_id)


@router.get("/{menu_id}/processes", response_model=list[ProcessOut])
def list_menu_processes(
    menu_id: int,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    menu = svc.get_by_id(menu_id)
    return menu.processes


@router.post(
    "/{menu_id}/processes/{process_id}",
    response_model=MenuOut,
    status_code=status.HTTP_200_OK,
)
def assign_process(
    menu_id: int,
    process_id: int,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.assign_process(menu_id, process_id)


@router.delete(
    "/{menu_id}/processes/{process_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_process(
    menu_id: int,
    process_id: int,
    svc: MenuService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.remove_process(menu_id, process_id)