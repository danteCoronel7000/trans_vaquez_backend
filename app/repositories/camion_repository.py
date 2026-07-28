from sqlalchemy.orm import Session, joinedload
from app.models.camion import Camion
from app.repositories.base import BaseRepository


class CamionRepository(BaseRepository[Camion]):
    def __init__(self, db: Session):
        super().__init__(Camion, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Camion]:
        return (
            self.db.query(Camion)
            .options(joinedload(Camion.image))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, camion_id: int) -> Camion | None:
        return (
            self.db.query(Camion)
            .options(joinedload(Camion.image))
            .filter(Camion.id == camion_id)
            .first()
        )

    def get_by_placa(self, placa: str) -> Camion | None:
        return self.db.query(Camion).filter(Camion.placa == placa).first()

    def get_by_numero_chasis(self, numero_chasis: str) -> Camion | None:
        return self.db.query(Camion).filter(Camion.numero_chasis == numero_chasis).first()

    def get_by_numero_motor(self, numero_motor: str) -> Camion | None:
        return self.db.query(Camion).filter(Camion.numero_motor == numero_motor).first()