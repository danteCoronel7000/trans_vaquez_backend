from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.schemas.camion import CamionCreate, CamionUpdate, CamionOut
from app.services.camion_service import CamionService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> CamionService:
    return CamionService(db)


def parse_camion_create(camion: str) -> CamionCreate:
    try:
        return CamionCreate.model_validate_json(camion)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(include_url=False, include_context=False),
        )


async def read_optional_image(
    file: UploadFile | None,
) -> tuple[bytes | None, str | None]:
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


@router.get("/", response_model=list[CamionOut])
def list_camiones(
    skip: int = 0,
    limit: int = 100,
    svc: CamionService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_all(skip, limit)


@router.post("/", response_model=CamionOut, status_code=status.HTTP_201_CREATED)
async def create_camion(
    camion: str = Form(..., description="JSON con los datos de CamionCreate"),
    file: UploadFile | None = File(None, description="Imagen opcional"),
    svc: CamionService = Depends(get_service),
    _=Depends(get_current_user),
):
    data = parse_camion_create(camion)
    file_bytes, filename = await read_optional_image(file)
    return svc.create(data, file_bytes, filename)


@router.get("/{camion_id}", response_model=CamionOut)
def get_camion(
    camion_id: int,
    svc: CamionService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_id(camion_id)


@router.patch("/{camion_id}", response_model=CamionOut)
async def update_camion(
    camion_id: int,
    camion: str = Form(...),
    file: UploadFile | None = File(None),
    svc: CamionService = Depends(get_service),
    _=Depends(get_current_user),
):
    data = CamionUpdate.model_validate_json(camion)
    file_bytes, filename = await read_optional_image(file)
    return svc.update(camion_id, data, file_bytes, filename)


@router.delete("/{camion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camion(
    camion_id: int,
    svc: CamionService = Depends(get_service),
    _=Depends(get_current_user),
):
    svc.delete(camion_id)


@router.patch("/{camion_id}/toggle", response_model=CamionOut)
def toggle_active(
    camion_id: int,
    svc: CamionService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.toggle_active(camion_id)