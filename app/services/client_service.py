from sqlalchemy.orm import Session
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.repositories.person_repository import PersonRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.client import ClientCreate, ClientUpdate
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class ClientService:
    def __init__(self, db: Session):
        self.repo        = ClientRepository(db)
        self.person_repo = PersonRepository(db)
        self.role_repo   = RoleRepository(db)
        self.user_repo   = UserRepository(db)

    def create(self, data: ClientCreate) -> Client:
        # Verificar que la persona existe
        person = self.person_repo.get_by_id(data.person_id)
        if not person:
            raise NotFoundException(f"Persona con id {data.person_id} no encontrada")

        # Verificar que la persona no tenga ya un cliente
        if self.repo.get_by_person_id(data.person_id):
            raise ConflictException("La persona ya tiene un cliente registrado")

        # Crear el cliente con todos sus campos
        client = Client(
            person_id=    data.person_id,
            nit=          data.nit,
            razon_social= data.razon_social,
        )
        client = self.repo.create(client)

        # Asignar rol CLIENTE al user vinculado a la persona (si tiene user)
        user = person.user
        if user:
            role = self.role_repo.get_by_name("CLIENTE")
            if role and role not in user.roles:
                self.user_repo.assign_role(user, role)

        return client

    def get_all(self, skip: int, limit: int) -> list[Client]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, client_id: int) -> Client:
        client = self.repo.get_by_id(client_id)
        if not client:
            raise NotFoundException("Cliente no encontrado")
        return client

    def update(self, client_id: int, data: ClientUpdate) -> Client:
        client = self.get_by_id(client_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(client, field, value)
        return self.repo.update(client)

    def delete(self, client_id: int) -> None:
        client = self.get_by_id(client_id)
        self.repo.delete(client)

    def toggle_active(self, client_id: int) -> Client:
        client = self.get_by_id(client_id)
        client.is_active = not client.is_active
        return self.repo.update(client)