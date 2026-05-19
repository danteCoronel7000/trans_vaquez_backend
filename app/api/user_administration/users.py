from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserWithRoles, UserCreateWithPerson, UserListOut
from app.services.user_service import UserService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# ── Nuevo endpoint ────────────────────────────────────
@router.get(
    "/list",
    response_model=list[UserListOut]
)
def list_users_with_persons(
    skip: int = 0,
    limit: int = 100,
    svc: UserService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all_with_persons(skip, limit)

@router.get("/", response_model=list[UserOut])
def list_users(skip: int = 0, limit: int = 100, svc: UserService = Depends(get_service), _=Depends(get_current_user)):
    return svc.get_all(skip, limit)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, svc: UserService = Depends(get_service)):
    return svc.create(data)


@router.get("/{user_id}", response_model=UserWithRoles)
def get_user(user_id: int, svc: UserService = Depends(get_service), _=Depends(get_current_user)):
    return svc.get_by_id(user_id)


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, svc: UserService = Depends(get_service), _=Depends(get_current_user)):
    return svc.update(user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, svc: UserService = Depends(get_service), _=Depends(get_current_user)):
    svc.delete(user_id)


@router.post("/{user_id}/roles/{role_id}", response_model=UserOut)
def assign_role(user_id: int, role_id: int, svc: UserService = Depends(get_service), _=Depends(get_current_user)):
    return svc.assign_role(user_id, role_id)


@router.delete("/{user_id}/roles/{role_id}", response_model=UserOut)
def remove_role(user_id: int, role_id: int, svc: UserService = Depends(get_service), _=Depends(get_current_user)):
    return svc.remove_role(user_id, role_id)

@router.post(
    "/create-with-person",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
def create_user_with_person(
    data: UserCreateWithPerson,
    svc: UserService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create_with_person(data)