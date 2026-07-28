from sqlalchemy.orm import Session
from app.models.taller_mecanico import TallerMecanico
from app.repositories.taller_mecanico_repository import TallerMecanicoRepository
from app.schemas.taller_mecanico import TallerCreate, TallerUpdate
from app.exceptions.http_exceptions import NotFoundException


class TallerMecanicoService:
    def __init__(self, db: Session):
        self.repo = TallerMecanicoRepository(db)

    def create(self, data: TallerCreate) -> TallerMecanico:
        taller = TallerMecanico(**data.model_dump())
        return self.repo.create(taller)

    def get_all(self, skip: int, limit: int) -> list[TallerMecanico]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, taller_id: int) -> TallerMecanico:
        taller = self.repo.get_by_id(taller_id)
        if not taller:
            raise NotFoundException("Taller mecánico no encontrado")
        return taller

    def update(self, taller_id: int, data: TallerUpdate) -> TallerMecanico:
        taller = self.get_by_id(taller_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(taller, field, value)
        return self.repo.update(taller)

    def delete(self, taller_id: int) -> None:
        taller = self.get_by_id(taller_id)
        self.repo.delete(taller)

    def toggle_active(self, taller_id: int) -> TallerMecanico:
        taller = self.get_by_id(taller_id)
        taller.is_active = not taller.is_active
        return self.repo.update(taller)