from sqlalchemy.orm import Session
from app.models.chofer import Chofer
from app.repositories.chofer_repository import ChoferRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.chofer import ChoferCreate, ChoferUpdate
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class ChoferService:
    def __init__(self, db: Session):
        self.repo        = ChoferRepository(db)
        self.person_repo = PersonRepository(db)
        self.role_repo   = RoleRepository(db)
        self.user_repo   = UserRepository(db)

    def create(self, data: ChoferCreate) -> Chofer:
        # Verificar que la persona existe
        person = self.person_repo.get_by_id(data.person_id)
        if not person:
            raise NotFoundException(f"Persona con id {data.person_id} no encontrada")

        # Verificar que la persona no tenga ya un chofer
        if self.repo.get_by_person_id(data.person_id):
            raise ConflictException("La persona ya tiene un chofer registrado")

        # Verificar que la licencia no esté en uso
        if self.repo.get_by_licencia(data.licencia):
            raise ConflictException("El número de licencia ya está registrado")

        chofer = Chofer(
            person_id = data.person_id,
            licencia  = data.licencia,
            categoria = data.categoria,
        )
        chofer = self.repo.create(chofer)

        # Asignar rol CHOFER al user vinculado a la persona (si tiene user)
        user = person.user
        if user:
            role = self.role_repo.get_by_name("CHOFER")
            if role and role not in user.roles:
                self.user_repo.assign_role(user, role)

        return chofer

    def get_all(self, skip: int, limit: int) -> list[Chofer]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, chofer_id: int) -> Chofer:
        chofer = self.repo.get_by_id(chofer_id)
        if not chofer:
            raise NotFoundException("Chofer no encontrado")
        return chofer

    def update(self, chofer_id: int, data: ChoferUpdate) -> Chofer:
        chofer = self.get_by_id(chofer_id)

        # Verificar licencia única si se está actualizando
        if data.licencia and data.licencia != chofer.licencia:
            if self.repo.get_by_licencia(data.licencia):
                raise ConflictException("El número de licencia ya está registrado")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(chofer, field, value)
        return self.repo.update(chofer)

    def delete(self, chofer_id: int) -> None:
        chofer = self.get_by_id(chofer_id)
        self.repo.delete(chofer)

    def toggle_active(self, chofer_id: int) -> Chofer:
        chofer = self.get_by_id(chofer_id)
        chofer.is_active = not chofer.is_active
        return self.repo.update(chofer)