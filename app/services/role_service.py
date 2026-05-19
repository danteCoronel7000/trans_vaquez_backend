from sqlalchemy.orm import Session
from app.repositories.role_repository import RoleRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas.role import RoleCreate, RoleUpdate
from app.models.role import Role
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class RoleService:
    def __init__(self, db: Session):
        self.repo = RoleRepository(db)
        self.menu_repo = MenuRepository(db)

    def create(self, data: RoleCreate) -> Role:
        if self.repo.get_by_name(data.name):
            raise ConflictException("El nombre de rol ya existe")
        role = Role(**data.model_dump())
        return self.repo.create(role)

    def get_all(self, skip: int, limit: int) -> list[Role]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, role_id: int) -> Role:
        role = self.repo.get_by_id(role_id)
        if not role:
            raise NotFoundException("Rol no encontrado")
        return role

    def update(self, role_id: int, data: RoleUpdate) -> Role:
        role = self.get_by_id(role_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(role, field, value)
        return self.repo.update(role)

    def delete(self, role_id: int) -> None:
        role = self.get_by_id(role_id)
        self.repo.delete(role)

    def assign_menu(self, role_id: int, menu_id: int) -> Role:
        role = self.get_by_id(role_id)
        menu = self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("Menú no encontrado")
        return self.repo.assign_menu(role, menu)

    def remove_menu(self, role_id: int, menu_id: int) -> Role:
        role = self.get_by_id(role_id)
        menu = self.menu_repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("Menú no encontrado")
        return self.repo.remove_menu(role, menu)