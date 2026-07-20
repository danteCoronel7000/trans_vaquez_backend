from sqlalchemy.orm import Session
from app.core.cloudinary_service import cloudinary_service
from app.repositories.image_repository import ImageRepository
from app.repositories.person_repository import PersonRepository
from app.models.image import Image
from app.schemas.image import ImageOut
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class ImageService:
    def __init__(self, db: Session):
        self.repo        = ImageRepository(db)
        self.person_repo = PersonRepository(db)

    def upload(self, person_id: int, file_bytes: bytes, filename: str) -> Image:
        # Verificar que la persona existe
        person = self.person_repo.get_by_id(person_id)
        if not person:
            raise NotFoundException(f"Persona con id {person_id} no encontrada")

        # Si ya tiene imagen la reemplazamos
        # (elimina la anterior de Cloudinary y de la DB)
        existing = self.repo.get_by_person_id(person_id)
        if existing:
            self._delete_from_cloudinary(existing.image_id)
            self.repo.delete(existing)

        # Subir a Cloudinary
        result = cloudinary_service.upload(file_bytes, filename)

        # Guardar referencia en la DB
        image = Image(
            person_id = person_id,
            name      = filename,
            image_url = result.get("secure_url"),  # URL HTTPS
            image_id  = result.get("public_id"),   # ID para eliminar
        )
        return self.repo.create(image)

    def delete(self, person_id: int) -> None:
        image = self.repo.get_by_person_id(person_id)
        if not image:
            raise NotFoundException("La persona no tiene imagen registrada")
        self._delete_from_cloudinary(image.image_id)
        self.repo.delete(image)

    def get_by_person(self, person_id: int) -> Image:
        image = self.repo.get_by_person_id(person_id)
        if not image:
            raise NotFoundException("La persona no tiene imagen registrada")
        return image

    def _delete_from_cloudinary(self, public_id: str) -> None:
        if public_id:
            cloudinary_service.delete(public_id)