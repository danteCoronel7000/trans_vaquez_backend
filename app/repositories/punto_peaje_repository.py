from sqlalchemy.orm import Session
from app.models.punto_peaje import PuntoPeaje
from app.repositories.base import BaseRepository


class PuntoPeajeRepository(BaseRepository[PuntoPeaje]):
    def __init__(self, db: Session):
        super().__init__(PuntoPeaje, db)