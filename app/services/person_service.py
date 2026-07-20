from sqlalchemy.orm import Session
from app.repositories.person_repository import PersonRepository
from app.repositories.user_repository import UserRepository
from app.schemas.person import PersonCreate, PersonUpdate
from app.core.cloudinary_service import cloudinary_service
from app.models.image import Image
from app.models.person import Person
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class PersonService:
    def __init__(self, db: Session):
        self.repo = PersonRepository(db)
        self.user_repo = UserRepository(db)


    def _validate_create(self, data: PersonCreate, user_id: int | None = None) -> None:
        if user_id is not None:
            if not self.user_repo.get_by_id(user_id):
                raise NotFoundException("Usuario no encontrado")
            if self.repo.get_by_user_id(user_id):
                raise ConflictException("El usuario ya tiene datos personales registrados")

        if self.repo.get_by_ci(data.ci):
            raise ConflictException(f"La CI '{data.ci}' ya esta registrada")

    def assign_user(self, person_id: int, user_id: int) -> Person:
        person = self.get_by_id(person_id)
        if person.user_id is not None:
            raise ConflictException("La persona ya tiene un usuario asignado")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuario no encontrado")
        if self.repo.get_by_user_id(user_id):
            raise ConflictException("El usuario ya tiene datos personales registrados")

        person.user_id = user_id
        return self.repo.update(person)

    def unassign_user(self, person_id: int) -> Person:
        person = self.get_by_id(person_id)
        person.user_id = None
        return self.repo.update(person)

    def get_by_user_id(self, user_id: int) -> Person:
        person = self.repo.get_by_user_id(user_id)
        if not person:
            raise NotFoundException("Datos personales no encontrados para este usuario")
        return person

    def get_by_id(self, person_id: int) -> Person:
        person = self.repo.get_by_id(person_id)
        if not person:
            raise NotFoundException("Persona no encontrada")
        return person

    def update(self, user_id: int, data: PersonUpdate) -> Person:
        person = self.get_by_user_id(user_id)
        return self._update_person(person, data)

    # En PersonService
    def update_by_id(
        self,
        person_id: int,
        data: PersonUpdate,
        file_bytes: bytes | None = None,   # 👈 agregar
        filename: str | None = None,       # 👈 agregar
    ) -> Person:
        person = self.get_by_id(person_id)
        return self._update_person(person, data, file_bytes, filename)  # 👈 pasar al método interno

    def delete(self, user_id: int) -> None:
        person = self.get_by_user_id(user_id)
        self.repo.delete(person)

    # services/person_service.py
    def toggle_active(self, person_id: int) -> Person:
        return self.repo.toggle_active(person_id)

    def delete_by_id(self, person_id: int) -> None:
        person = self.get_by_id(person_id)
        self.repo.delete(person)

    def _update_person(
    self,
    person: Person,
    data: PersonUpdate,
    file_bytes: bytes | None = None,
    filename: str | None = None,
    ) -> Person:
    
        if data.ci and data.ci != person.ci:
            existing = self.repo.get_by_ci(data.ci)
    
            if existing:
                raise ConflictException(
                    f"La CI '{data.ci}' ya esta registrada"
                )
    
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(person, field, value)
    
        if file_bytes:
    
            if person.image and person.image.image_id:
                try:
                    cloudinary_service.delete(
                        person.image.image_id
                    )
                except Exception:
                    pass
    
            result = cloudinary_service.upload(
                file_bytes,
                filename or "image"
            )
    
            if person.image:
    
                person.image.name = filename or "image"
                person.image.image_url = result.get("secure_url")
                person.image.image_id = result.get("public_id")
    
            else:
    
                person.image = Image(
                    name=filename or "image",
                    image_url=result.get("secure_url"),
                    image_id=result.get("public_id"),
                )
    
        return self.repo.update(person)

    def create(
    self,
    data: PersonCreate,
    file_bytes: bytes | None = None,
    filename: str | None = None,
    user_id: int | None = None,
    ) -> Person:
        self._validate_create(data, user_id)
    
        uploaded_public_id: str | None = None
        # ✅ Si user_id ya no existe en el modelo Person
        person = Person(**data.model_dump())
    
        try:
            self.repo.db.add(person)
            self.repo.db.flush()
    
            if file_bytes:
                result = cloudinary_service.upload(
                    file_bytes,
                    filename or "image"
                )
    
                uploaded_public_id = result.get("public_id")
    
                person.image = Image(
                    name=filename or "image",
                    image_url=result.get("secure_url"),
                    image_id=uploaded_public_id,
                )
    
            self.repo.db.commit()
            self.repo.db.refresh(person)
    
            return person
    
        except Exception:
            self.repo.db.rollback()
    
            if uploaded_public_id:
                try:
                    cloudinary_service.delete(uploaded_public_id)
                except Exception:
                    pass
    
            raise      
