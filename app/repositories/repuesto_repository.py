from sqlalchemy.orm import Session
from app.models.repuesto import Repuesto
from app.repositories.base import BaseRepository


class RepuestoRepository(BaseRepository[Repuesto]):
    def __init__(self, db: Session):
        super().__init__(Repuesto, db)