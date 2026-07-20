from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas.image import ImageOut
from app.services.image_service import ImageService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ImageService:
    return ImageService(db)


@router.post(
    "/{person_id}",              # ← person_id va en la URL, no en query param
    response_model=ImageOut,
    status_code=status.HTTP_201_CREATED
)
async def upload_image(
    person_id: int,
    file: UploadFile = File(..., description="Imagen a subir"),
    svc: ImageService = Depends(get_service),
    _=Depends(get_current_user),
):
    # Validar que sea una imagen
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen (jpg, png, webp, etc.)"
        )

    file_bytes = await file.read()
    return svc.upload(person_id, file_bytes, file.filename or "image")

@router.get("/{person_id}", response_model=ImageOut)
def get_image(
    person_id: int,
    svc: ImageService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.get_by_person(person_id)


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    person_id: int,
    svc: ImageService = Depends(get_service),
    _=Depends(get_current_user),
):
    """
    Elimina la imagen de Cloudinary y de la DB.
    Equivalente al deleteImage() de Spring Boot.
    """
    svc.delete(person_id)