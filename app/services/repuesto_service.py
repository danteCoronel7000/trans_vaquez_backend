from sqlalchemy.orm import Session
from app.models.repuesto import Repuesto
from app.repositories.repuesto_repository import RepuestoRepository
from app.schemas.repuesto import RepuestoCreate, RepuestoUpdate
from app.exceptions.http_exceptions import NotFoundException


class RepuestoService:
    def __init__(self, db: Session):
        self.repo = RepuestoRepository(db)

    def create(self, data: RepuestoCreate) -> Repuesto:
        repuesto = Repuesto(**data.model_dump())
        return self.repo.create(repuesto)

    def get_all(self, skip: int, limit: int) -> list[Repuesto]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, repuesto_id: int) -> Repuesto:
        repuesto = self.repo.get_by_id(repuesto_id)
        if not repuesto:
            raise NotFoundException("Repuesto no encontrado")
        return repuesto

    def update(self, repuesto_id: int, data: RepuestoUpdate) -> Repuesto:
        repuesto = self.get_by_id(repuesto_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(repuesto, field, value)
        return self.repo.update(repuesto)

    def delete(self, repuesto_id: int) -> None:
        repuesto = self.get_by_id(repuesto_id)
        self.repo.delete(repuesto)