from sqlalchemy.orm import Session
from app.models.informacion_carga import InformacionCarga
from app.repositories.base import BaseRepository


class InformacionCargaRepository(BaseRepository[InformacionCarga]):
    def __init__(self, db: Session):
        super().__init__(InformacionCarga, db)