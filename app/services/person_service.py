from sqlalchemy.orm import Session
from app.repositories.person_repository import PersonRepository
from app.repositories.user_repository import UserRepository
from app.schemas.person import PersonCreate, PersonUpdate
from app.models.person import Person
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class PersonService:
    def __init__(self, db: Session):
        self.repo = PersonRepository(db)
        self.user_repo = UserRepository(db)

    def create(self, data: PersonCreate, user_id: int | None = None) -> Person:
        if user_id is not None:
            if not self.user_repo.get_by_id(user_id):
                raise NotFoundException("Usuario no encontrado")
            if self.repo.get_by_user_id(user_id):
                raise ConflictException("El usuario ya tiene datos personales registrados")

        if self.repo.get_by_ci(data.ci):
            raise ConflictException(f"La CI '{data.ci}' ya esta registrada")

        person = Person(user_id=user_id, **data.model_dump())
        return self.repo.create(person)

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

    def update_by_id(self, person_id: int, data: PersonUpdate) -> Person:
        person = self.get_by_id(person_id)
        return self._update_person(person, data)

    def delete(self, user_id: int) -> None:
        person = self.get_by_user_id(user_id)
        self.repo.delete(person)

    def delete_by_id(self, person_id: int) -> None:
        person = self.get_by_id(person_id)
        self.repo.delete(person)

    def _update_person(self, person: Person, data: PersonUpdate) -> Person:
        if data.ci and data.ci != person.ci:
            existing = self.repo.get_by_ci(data.ci)
            if existing:
                raise ConflictException(f"La CI '{data.ci}' ya esta registrada")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(person, field, value)
        return self.repo.update(person)
