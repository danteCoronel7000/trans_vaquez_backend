from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.schemas.person import PersonCreate, PersonUpdate, PersonOut, ToggleActiveOut
from app.services.person_service import PersonService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

user_person_router = APIRouter()
persons_router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> PersonService:
    return PersonService(db)


def parse_person_create(person: str) -> PersonCreate:
    try:
        return PersonCreate.model_validate_json(person)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(include_url=False, include_context=False),
        )


async def read_optional_image(file: UploadFile | None) -> tuple[bytes | None, str | None]:
    if file is None or not file.filename:
        return None, None

    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser una imagen (jpg, png, webp, etc.)",
        )

    file_bytes = await file.read()
    if not file_bytes:
        return None, None

    return file_bytes, file.filename


@user_person_router.post(
    "/",
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_person(
    user_id: int,
    person: str = Form(..., description="JSON con los datos de PersonCreate"),
    file: UploadFile | None = File(None, description="Imagen opcional"),
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    data = parse_person_create(person)

    file_bytes, filename = await read_optional_image(file)

    return svc.create(
        data,
        file_bytes,
        filename,
        user_id=user_id,
    )


@user_person_router.get("/", response_model=PersonOut)
def get_person(
    user_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_user_id(user_id)


@user_person_router.patch("/", response_model=PersonOut)
async def update_person(
    user_id: int,
    person: str = Form(...),
    file: UploadFile | None = File(None),
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    data = PersonUpdate.model_validate_json(person)

    file_bytes, filename = await read_optional_image(file)

    return svc.update(
        user_id,
        data,
        file_bytes,
        filename,
    )


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
async def create_unassigned_person(
    person: str = Form(..., description="JSON con los datos de PersonCreate"),
    file: UploadFile | None = File(None, description="Imagen opcional"),
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    data = parse_person_create(person)

    file_bytes, filename = await read_optional_image(file)

    return svc.create(
        data,
        file_bytes,
        filename,
    )

@persons_router.get("/{person_id}", response_model=PersonOut)
def get_person_by_id(
    person_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(person_id)

# persons.py
@persons_router.patch(
    "/{person_id}/toggle-active",
    response_model=ToggleActiveOut,
)
async def toggle_person_active(
    person_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(person_id)


@persons_router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person_by_id(
    person_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete_by_id(person_id)


@persons_router.patch(
    "/{person_id}",
    response_model=PersonOut,
)
async def update_person_by_id(
    person_id: int,
    person: str = Form(...),
    file: UploadFile | None = File(None),
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    data = PersonUpdate.model_validate_json(person)

    file_bytes, filename = await read_optional_image(file)

    return svc.update_by_id(
        person_id,
        data,
        file_bytes,
        filename,
    )


@persons_router.delete("/{person_id}/user", response_model=PersonOut)
def unassign_user_from_person(
    person_id: int,
    svc: PersonService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.unassign_user(person_id)
