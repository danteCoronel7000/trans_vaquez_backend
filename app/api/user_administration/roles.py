from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut
from app.schemas.menu import MenuOut
from app.services.role_service import RoleService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)


@router.get("/", response_model=list[RoleOut])
def list_roles(
    skip: int = 0,
    limit: int = 100,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    data: RoleCreate,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: int,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(role_id)


@router.patch("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    data: RoleUpdate,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(role_id, data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(role_id)


@router.get("/{role_id}/menus", response_model=list[MenuOut])
def list_role_menus(
    role_id: int,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    role = svc.get_by_id(role_id)
    return role.menus


@router.post(
    "/{role_id}/menus/{menu_id}",
    response_model=RoleOut,
    status_code=status.HTTP_200_OK,
)
def assign_menu(
    role_id: int,
    menu_id: int,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.assign_menu(role_id, menu_id)


@router.delete("/{role_id}/menus/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_menu(
    role_id: int,
    menu_id: int,
    svc: RoleService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.remove_menu(role_id, menu_id)