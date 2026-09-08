from sqlalchemy.orm import Session
from app.models.tipo_servicio import TipoServicio
from app.repositories.tipo_servicio_repository import TipoServicioRepository
from app.schemas.tipo_servicio import TipoServicioCreate, TipoServicioUpdate
from app.exceptions.http_exceptions import NotFoundException


class TipoServicioService:
    def __init__(self, db: Session):
        self.repo = TipoServicioRepository(db)

    def create(self, data: TipoServicioCreate) -> TipoServicio:
        tipo = TipoServicio(**data.model_dump())
        return self.repo.create(tipo)

    def get_all(self, skip: int, limit: int) -> list[TipoServicio]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, tipo_id: int) -> TipoServicio:
        tipo = self.repo.get_by_id(tipo_id)
        if not tipo:
            raise NotFoundException("Tipo de servicio no encontrado")
        return tipo

    def update(self, tipo_id: int, data: TipoServicioUpdate) -> TipoServicio:
        tipo = self.get_by_id(tipo_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(tipo, field, value)
        return self.repo.update(tipo)

    def delete(self, tipo_id: int) -> None:
        tipo = self.get_by_id(tipo_id)
        self.repo.delete(tipo)

    def toggle_active(self, tipo_id: int) -> TipoServicio:
        tipo = self.get_by_id(tipo_id)
        tipo.is_active = not tipo.is_active
        return self.repo.update(tipo)