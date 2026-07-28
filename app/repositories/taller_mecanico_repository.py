from sqlalchemy.orm import Session
from app.models.taller_mecanico import TallerMecanico
from app.repositories.base import BaseRepository


class TallerMecanicoRepository(BaseRepository[TallerMecanico]):
    def __init__(self, db: Session):
        super().__init__(TallerMecanico, db)