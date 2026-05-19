from sqlalchemy.orm import Session
from app.repositories.menu_repository import MenuRepository
from app.repositories.process_repository import ProcessRepository
from app.schemas.menu import MenuCreate, MenuUpdate
from app.models.menu import Menu
from app.exceptions.http_exceptions import NotFoundException


class MenuService:
    def __init__(self, db: Session):
        self.repo = MenuRepository(db)
        self.process_repo = ProcessRepository(db)

    def create(self, data: MenuCreate) -> Menu:
        menu = Menu(**data.model_dump())
        return self.repo.create(menu)

    def get_all(self, skip: int, limit: int) -> list[Menu]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, menu_id: int) -> Menu:
        menu = self.repo.get_by_id(menu_id)
        if not menu:
            raise NotFoundException("Menú no encontrado")
        return menu

    def update(self, menu_id: int, data: MenuUpdate) -> Menu:
        menu = self.get_by_id(menu_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(menu, field, value)
        return self.repo.update(menu)

    def delete(self, menu_id: int) -> None:
        menu = self.get_by_id(menu_id)
        self.repo.delete(menu)

    def assign_process(self, menu_id: int, process_id: int) -> Menu:
        menu = self.get_by_id(menu_id)
        process = self.process_repo.get_by_id(process_id)
        if not process:
            raise NotFoundException("Proceso no encontrado")
        return self.repo.assign_process(menu, process)

    def remove_process(self, menu_id: int, process_id: int) -> Menu:
        menu = self.get_by_id(menu_id)
        process = self.process_repo.get_by_id(process_id)
        if not process:
            raise NotFoundException("Proceso no encontrado")
        return self.repo.remove_process(menu, process)