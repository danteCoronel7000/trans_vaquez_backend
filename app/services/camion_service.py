from sqlalchemy.orm import Session
from app.models.camion import Camion
from app.models.image import Image
from app.repositories.camion_repository import CamionRepository
from app.schemas.camion import CamionCreate, CamionUpdate
from app.exceptions.http_exceptions import NotFoundException, ConflictException
from app.core.cloudinary_service import cloudinary_service


class CamionService:
    def __init__(self, db: Session):
        self.repo = CamionRepository(db)

    def _validate_unique_fields(
        self,
        data: CamionCreate | CamionUpdate,
        exclude_id: int | None = None
    ) -> None:
        if data.placa:
            existing = self.repo.get_by_placa(data.placa)
            if existing and existing.id != exclude_id:
                raise ConflictException("La placa ya está registrada")

        if data.numero_chasis:
            existing = self.repo.get_by_numero_chasis(data.numero_chasis)
            if existing and existing.id != exclude_id:
                raise ConflictException("El número de chasis ya está registrado")

        if data.numero_motor:
            existing = self.repo.get_by_numero_motor(data.numero_motor)
            if existing and existing.id != exclude_id:
                raise ConflictException("El número de motor ya está registrado")

    def create(
        self,
        data: CamionCreate,
        file_bytes: bytes | None = None,
        filename: str | None = None,
    ) -> Camion:
        self._validate_unique_fields(data)

        uploaded_public_id: str | None = None
        camion = Camion(**data.model_dump())

        try:
            self.repo.db.add(camion)
            self.repo.db.flush()

            if file_bytes:
                result = cloudinary_service.upload(file_bytes, filename or "camion")
                uploaded_public_id = result.get("public_id")
                camion.image = Image(
                    name=filename or "camion",
                    image_url=result.get("secure_url"),
                    image_id=uploaded_public_id,
                    camion_id=camion.id,
                )

            self.repo.db.commit()
            self.repo.db.refresh(camion)
            return camion

        except Exception:
            self.repo.db.rollback()
            if uploaded_public_id:
                try:
                    cloudinary_service.delete(uploaded_public_id)
                except Exception:
                    pass
            raise

    def get_all(self, skip: int, limit: int) -> list[Camion]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, camion_id: int) -> Camion:
        camion = self.repo.get_by_id(camion_id)
        if not camion:
            raise NotFoundException("Camión no encontrado")
        return camion

    def update(
        self,
        camion_id: int,
        data: CamionUpdate,
        file_bytes: bytes | None = None,
        filename: str | None = None,
    ) -> Camion:
        camion = self.get_by_id(camion_id)
        self._validate_unique_fields(data, exclude_id=camion_id)

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(camion, field, value)

        uploaded_public_id: str | None = None

        try:
            if file_bytes:
                # Eliminar imagen anterior si existe
                if camion.image and camion.image.image_id:
                    try:
                        cloudinary_service.delete(camion.image.image_id)
                    except Exception:
                        pass

                result = cloudinary_service.upload(file_bytes, filename or "camion")
                uploaded_public_id = result.get("public_id")

                if camion.image:
                    camion.image.name      = filename or "camion"
                    camion.image.image_url = result.get("secure_url")
                    camion.image.image_id  = uploaded_public_id
                else:
                    camion.image = Image(
                        name=filename or "camion",
                        image_url=result.get("secure_url"),
                        image_id=uploaded_public_id,
                        camion_id=camion.id,
                    )

            self.repo.db.commit()
            self.repo.db.refresh(camion)
            return camion

        except Exception:
            self.repo.db.rollback()
            if uploaded_public_id:
                try:
                    cloudinary_service.delete(uploaded_public_id)
                except Exception:
                    pass
            raise

    def delete(self, camion_id: int) -> None:
        camion = self.get_by_id(camion_id)
        if camion.image and camion.image.image_id:
            try:
                cloudinary_service.delete(camion.image.image_id)
            except Exception:
                pass
        self.repo.delete(camion)

    def toggle_active(self, camion_id: int) -> Camion:
        camion = self.get_by_id(camion_id)
        camion.is_active = not camion.is_active
        return self.repo.update(camion)