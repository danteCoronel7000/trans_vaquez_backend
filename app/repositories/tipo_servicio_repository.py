from sqlalchemy.orm import Session
from app.models.tipo_servicio import TipoServicio
from app.repositories.base import BaseRepository


class TipoServicioRepository(BaseRepository[TipoServicio]):
    def __init__(self, db: Session):
        super().__init__(TipoServicio, db)