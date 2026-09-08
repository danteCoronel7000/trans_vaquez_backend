from sqlalchemy.orm import Session
from app.models.punto_carga_combustible import PuntoCargaCombustible
from app.repositories.punto_carga_combustible_repository import PuntoCargaCombustibleRepository
from app.schemas.punto_carga_combustible import PuntoCargaCreate, PuntoCargaUpdate
from app.exceptions.http_exceptions import NotFoundException


class PuntoCargaCombustibleService:
    def __init__(self, db: Session):
        self.repo = PuntoCargaCombustibleRepository(db)

    def create(self, data: PuntoCargaCreate) -> PuntoCargaCombustible:
        punto = PuntoCargaCombustible(**data.model_dump())
        return self.repo.create(punto)

    def get_all(self, skip: int, limit: int) -> list[PuntoCargaCombustible]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, punto_id: int) -> PuntoCargaCombustible:
        punto = self.repo.get_by_id(punto_id)
        if not punto:
            raise NotFoundException("Punto de carga de combustible no encontrado")
        return punto

    def update(self, punto_id: int, data: PuntoCargaUpdate) -> PuntoCargaCombustible:
        punto = self.get_by_id(punto_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(punto, field, value)
        return self.repo.update(punto)

    def toggle_active(self, punto_id: int) -> PuntoCargaCombustible:
        punto = self.get_by_id(punto_id)
        punto.is_active = not punto.is_active
        return self.repo.update(punto)

    def delete(self, punto_id: int) -> None:
        punto = self.get_by_id(punto_id)
        self.repo.delete(punto)