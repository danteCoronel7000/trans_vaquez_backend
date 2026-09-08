from sqlalchemy.orm import Session
from app.models.ruta import Ruta
from app.repositories.ruta_repository import RutaRepository
from app.repositories.punto_peaje_repository import PuntoPeajeRepository
from app.repositories.punto_carga_combustible_repository import PuntoCargaCombustibleRepository
from app.schemas.ruta import RutaCreate, RutaUpdate
from app.exceptions.http_exceptions import NotFoundException, ConflictException


class RutaService:
    def __init__(self, db: Session):
        self.repo             = RutaRepository(db)
        self.peaje_repo       = PuntoPeajeRepository(db)
        self.punto_carga_repo = PuntoCargaCombustibleRepository(db)

    def create(self, data: RutaCreate) -> Ruta:
        ruta = Ruta(**data.model_dump())
        return self.repo.create(ruta)

    def get_all(self, skip: int, limit: int) -> list[Ruta]:
        return self.repo.get_all(skip, limit)

    def get_by_id(self, ruta_id: int) -> Ruta:
        ruta = self.repo.get_by_id(ruta_id)
        if not ruta:
            raise NotFoundException("Ruta no encontrada")
        return ruta

    def update(self, ruta_id: int, data: RutaUpdate) -> Ruta:
        ruta = self.get_by_id(ruta_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(ruta, field, value)
        return self.repo.update(ruta)

    def delete(self, ruta_id: int) -> None:
        ruta = self.get_by_id(ruta_id)
        self.repo.delete(ruta)

    def toggle_active(self, ruta_id: int) -> Ruta:
        ruta = self.get_by_id(ruta_id)
        ruta.is_active = not ruta.is_active
        return self.repo.update(ruta)

    # Gestión de peajes
    def assign_peaje(self, ruta_id: int, peaje_id: int) -> Ruta:
        ruta = self.get_by_id(ruta_id)
        peaje = self.peaje_repo.get_by_id(peaje_id)
        if not peaje:
            raise NotFoundException("Punto de peaje no encontrado")
        if peaje in ruta.peajes:
            raise ConflictException("El punto de peaje ya está asignado a esta ruta")
        ruta.peajes.append(peaje)
        self.repo.db.commit()
        self.repo.db.refresh(ruta)
        return ruta

    def remove_peaje(self, ruta_id: int, peaje_id: int) -> Ruta:
        ruta = self.get_by_id(ruta_id)
        peaje = self.peaje_repo.get_by_id(peaje_id)
        if not peaje or peaje not in ruta.peajes:
            raise NotFoundException("El punto de peaje no está asignado a esta ruta")
        ruta.peajes.remove(peaje)
        self.repo.db.commit()
        self.repo.db.refresh(ruta)
        return ruta

    # Gestión de puntos de carga
    def assign_punto_carga(self, ruta_id: int, punto_id: int) -> Ruta:
        ruta = self.get_by_id(ruta_id)
        punto = self.punto_carga_repo.get_by_id(punto_id)
        if not punto:
            raise NotFoundException("Punto de carga de combustible no encontrado")
        if punto in ruta.puntos_carga:
            raise ConflictException("El punto de carga ya está asignado a esta ruta")
        ruta.puntos_carga.append(punto)
        self.repo.db.commit()
        self.repo.db.refresh(ruta)
        return ruta

    def remove_punto_carga(self, ruta_id: int, punto_id: int) -> Ruta:
        ruta = self.get_by_id(ruta_id)
        punto = self.punto_carga_repo.get_by_id(punto_id)
        if not punto or punto not in ruta.puntos_carga:
            raise NotFoundException("El punto de carga no está asignado a esta ruta")
        ruta.puntos_carga.remove(punto)
        self.repo.db.commit()
        self.repo.db.refresh(ruta)
        return ruta