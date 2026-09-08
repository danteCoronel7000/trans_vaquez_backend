from sqlalchemy.orm import Session
from app.models.punto_carga_combustible import PuntoCargaCombustible
from app.repositories.base import BaseRepository


class PuntoCargaCombustibleRepository(BaseRepository[PuntoCargaCombustible]):
    def __init__(self, db: Session):
        super().__init__(PuntoCargaCombustible, db)