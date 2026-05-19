from sqlalchemy.orm import Session
from app.models.process import Process
from app.repositories.base import BaseRepository


class ProcessRepository(BaseRepository[Process]):
    def __init__(self, db: Session):
        super().__init__(Process, db)

    def get_by_code(self, code: str) -> Process | None:
        return self.db.query(Process).filter(Process.code == code).first()