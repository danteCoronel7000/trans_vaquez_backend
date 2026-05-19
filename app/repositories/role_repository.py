from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.menu import Menu
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)

    def get_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()

    def assign_menu(self, role: Role, menu: Menu) -> Role:
        if menu not in role.menus:
            role.menus.append(menu)
            self.db.commit()
            self.db.refresh(role)
        return role

    def remove_menu(self, role: Role, menu: Menu) -> Role:
        if menu in role.menus:
            role.menus.remove(menu)
            self.db.commit()
            self.db.refresh(role)
        return role