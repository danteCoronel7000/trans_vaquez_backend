from sqlalchemy.orm import Session
from app.models.menu import Menu
from app.models.process import Process
from app.repositories.base import BaseRepository


class MenuRepository(BaseRepository[Menu]):
    def __init__(self, db: Session):
        super().__init__(Menu, db)

    def assign_process(self, menu: Menu, process: Process) -> Menu:
        if process not in menu.processes:
            menu.processes.append(process)
            self.db.commit()
            self.db.refresh(menu)
        return menu

    def remove_process(self, menu: Menu, process: Process) -> Menu:
        if process in menu.processes:
            menu.processes.remove(process)
            self.db.commit()
            self.db.refresh(menu)
        return menu