from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.person_repository import PersonRepository
from app.schemas.user import UserCreate, UserCreateWithPerson, UserUpdate
from app.models.user import User
from app.core.security import hash_password
from app.exceptions.http_exceptions import NotFoundException, ConflictException
from app.repositories.user_system_repository import UserSystemRepository
from app.models.user_system import UserSystem

# Roles que crean registro en user_system
SYSTEM_ROLES = {"ADMIN", "ENCARGADO", "DUEÑO"}

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.user_system_repo = UserSystemRepository(db)  # ✅ agregar

    def create(self, data: UserCreate) -> User:
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
   
           if not role.is_active:
               raise ConflictException(f"El rol '{role.name}' está deshabilitado y no puede asignarse")
   
           if role in user.roles:
               raise ConflictException(f"El rol '{role.name}' ya está asignado a este usuario")
   
           # Asignar el rol
           result = self.repo.assign_role(user, role)
   
           # Si el rol es de sistema y la persona no tiene ya un user_system, crearlo
           if role.name.upper() in SYSTEM_ROLES:
               person = user.person
               if person:
                   already_exists = self.user_system_repo.get_by_person_id(person.id)
                   if not already_exists:
                       # Verificar que ningún rol de sistema ya estaba asignado antes
                       existing_system_roles = [
                           r for r in user.roles
                           if r.name.upper() in SYSTEM_ROLES and r.id != role_id
                       ]
                       if not existing_system_roles:
                           user_system = UserSystem(person_id=person.id)
                           self.user_system_repo.create(user_system)
   
           return result
    
    
    def remove_role(self, user_id: int, role_id: int) -> User:
        user = self.get_by_id(user_id)  # Excepción 3: usuario no encontrado
    
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Rol no encontrado")
    
        # Rol no estaba asignado
        if role not in user.roles:
            raise ConflictException(f"El rol '{role.name}' no está asignado a este usuario")
    
        return self.repo.remove_role(user, role)
    
    
    # services/user_service.py
    def toggle_active(self, id: int) -> User:
        return self.repo.toggle_active(id)
    
    def create_with_person(self, data: UserCreateWithPerson) -> User:
        if self.repo.get_by_username(data.username):
            raise ConflictException("El username ya está en uso")
    
        # Verificar que la persona existe
        person_repo = PersonRepository(self.repo.db)
        person = person_repo.get_by_id(data.id_persona)
        if not person:
            raise NotFoundException(f"Persona con id {data.id_persona} no encontrada")
    
        # ✅ CAMBIO: verificar que la persona no tenga ya un usuario
        # ya no es person.user_id, ahora se verifica desde el lado User
        if person.user:
            raise ConflictException("La persona ya tiene un usuario asignado")
    
        # ✅ CAMBIO: person_id va directo en la creación del User
        user = User(
            username  = data.username,
            password  = hash_password(data.password),
            person_id = data.id_persona  # ← FK ahora en User
        )
        return self.repo.create(user)