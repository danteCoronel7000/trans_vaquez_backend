from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.person_repository import PersonRepository
from app.schemas.user import UserCreate, UserUpdate, UserCreateWithPerson, UserListOut
from app.models.user import User
from app.core.security import hash_password
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    def create(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise ConflictException("El email ya está registrado")
        if self.repo.get_by_username(data.username):
            raise ConflictException("El username ya está en uso")
        user = User(**data.model_dump(exclude={"password"}), password=hash_password(data.password))
        return self.repo.create(user)

    def get_all(self, skip: int, limit: int) -> list[User]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuario no encontrado")
        return user

    def update(self, user_id: int, data: UserUpdate) -> User:
        user = self.get_by_id(user_id)
        for field, value in data.model_dump(exclude_none=True).items():
            if field == "password":
                value = hash_password(value)
            setattr(user, field, value)
        return self.repo.update(user)

    def delete(self, user_id: int) -> None:
        user = self.get_by_id(user_id)
        self.repo.delete(user)

    def assign_role(self, user_id: int, role_id: int) -> User:
        user = self.get_by_id(user_id)
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Rol no encontrado")
        return self.repo.assign_role(user, role)

    def remove_role(self, user_id: int, role_id: int) -> User:
        user = self.get_by_id(user_id)
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Rol no encontrado")
        return self.repo.remove_role(user, role)
    
    def create_with_person(self, data: UserCreateWithPerson) -> User:
    # Verificar email y username únicos
        if self.repo.get_by_email(data.email):
            raise ConflictException("El email ya está registrado")
        if self.repo.get_by_username(data.username):
            raise ConflictException("El username ya está en uso")

    # Verificar que la persona existe
        person_repo = PersonRepository(self.repo.db)
        person = person_repo.get_by_id(data.id_persona)
        if not person:
            raise NotFoundException(f"Persona con id {data.id_persona} no encontrada")

    # Verificar que la persona no tenga ya un usuario
        if person.user_id:
            raise ConflictException("La persona ya tiene un usuario asignado")

    # Crear el usuario
        user = User(
            username  = data.username,
            email     = data.email,
            password  = hash_password(data.password)
        )
        user = self.repo.create(user)

    # Vincular la persona al usuario recién creado
        person.user_id = user.id
        person_repo.update(person)

        return user
    
    def get_all_with_persons(
    self, skip: int = 0, limit: int = 100
    ) -> list[UserListOut]:
        users = self.repo.get_all_with_persons(skip, limit)
        return [UserListOut.from_user(u) for u in users]
