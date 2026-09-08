from sqlalchemy.orm import Session
from app.models.punto_peaje import PuntoPeaje
from app.repositories.punto_peaje_repository import PuntoPeajeRepository
from app.schemas.punto_peaje import PuntoPeajeCreate, PuntoPeajeUpdate
from app.exceptions.http_exceptions import NotFoundException


class PuntoPeajeService:
    def __init__(self, db: Session):
        self.repo = PuntoPeajeRepository(db)

    def create(self, data: PuntoPeajeCreate) -> PuntoPeaje:
        punto = PuntoPeaje(**data.model_dump())
        return self.repo.create(punto)

    def get_all(self, skip: int, limit: int) -> list[PuntoPeaje]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, punto_id: int) -> PuntoPeaje:
        punto = self.repo.get_by_id(punto_id)
        if not punto:
            raise NotFoundException("Punto de peaje no encontrado")
        return punto

    def update(self, punto_id: int, data: PuntoPeajeUpdate) -> PuntoPeaje:
        punto = self.get_by_id(punto_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(punto, field, value)
        return self.repo.update(punto)

    def toggle_active(self, punto_id: int) -> PuntoPeaje:
        punto = self.get_by_id(punto_id)
        punto.is_active = not punto.is_active
        return self.repo.update(punto)

    def delete(self, punto_id: int) -> None:
        punto = self.get_by_id(punto_id)
        self.repo.delete(punto)