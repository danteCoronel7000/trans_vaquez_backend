from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.person import PersonCreate, PersonUpdate, PersonOut
from app.services.person_service import PersonService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

user_person_router = APIRouter()
persons_router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> PersonService:
    return PersonService(db)


@user_person_router.post(
    "/",
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED
)
def create_person(
    user_id: int,
    data: PersonCreate,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data, user_id=user_id)


@user_person_router.get("/", response_model=PersonOut)
def get_person(
    user_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_user_id(user_id)


@user_person_router.patch("/", response_model=PersonOut)
def update_person(
    user_id: int,
    data: PersonUpdate,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update(user_id, data)


@user_person_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    user_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(user_id)

@persons_router.get("/", response_model=list[PersonOut])
def list_persons(
    skip: int = 0,
    limit: int = 500,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.repo.get_all(skip, limit)


@persons_router.post(
    "/",
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
)
def create_unassigned_person(
    data: PersonCreate,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.create(data)


@persons_router.get("/{person_id}", response_model=PersonOut)
def get_person_by_id(
    person_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(person_id)


@persons_router.patch("/{person_id}", response_model=PersonOut)
def update_person_by_id(
    person_id: int,
    data: PersonUpdate,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.update_by_id(person_id, data)


@persons_router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person_by_id(
    person_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete_by_id(person_id)


@persons_router.patch("/{person_id}/user/{user_id}", response_model=PersonOut)
def assign_user_to_person(
    person_id: int,
    user_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.assign_user(person_id, user_id)


@persons_router.delete("/{person_id}/user", response_model=PersonOut)
def unassign_user_from_person(
    person_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.unassign_user(person_id)
