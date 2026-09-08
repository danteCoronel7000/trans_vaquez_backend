from sqlalchemy.orm import Session, joinedload
from app.models.ruta import Ruta
from app.repositories.base import BaseRepository


class RutaRepository(BaseRepository[Ruta]):
    def __init__(self, db: Session):
        super().__init__(Ruta, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Ruta]:
        return (
            self.db.query(Ruta)
            .options(joinedload(Ruta.peajes), joinedload(Ruta.puntos_carga))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, ruta_id: int) -> Ruta | None:
        return (
            self.db.query(Ruta)
            .options(joinedload(Ruta.peajes), joinedload(Ruta.puntos_carga))
            .filter(Ruta.id == ruta_id)
            .first()
        )