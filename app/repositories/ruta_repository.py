from sqlalchemy.orm import Session, joinedload
from app.models.ruta import Ruta
from app.models.servicio_transporte import ServicioTransporte, EstadoServicioEnum
from app.repositories.base import BaseRepository

# Estados que mantienen a una ruta "en uso"
ESTADOS_EN_USO = (EstadoServicioEnum.PROGRAMADO, EstadoServicioEnum.EN_CURSO)


class RutaRepository(BaseRepository[Ruta]):
    def __init__(self, db: Session):
        super().__init__(Ruta, db)

    def _ids_en_uso(self, ruta_ids: list[int]) -> set[int]:
        """Devuelve los ids de rutas que tienen servicios programados o en curso."""
        if not ruta_ids:
            return set()
        filas = (
            self.db.query(ServicioTransporte.id_ruta)
            .filter(
                ServicioTransporte.id_ruta.in_(ruta_ids),
                ServicioTransporte.estado.in_(ESTADOS_EN_USO),
            )
            .distinct()
            .all()
        )
        return {fila[0] for fila in filas}

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Ruta]:
        rutas = (
            self.db.query(Ruta)
            .options(joinedload(Ruta.peajes), joinedload(Ruta.puntos_carga))
            .offset(skip)
            .limit(limit)
            .all()
        )
        en_uso = self._ids_en_uso([r.id for r in rutas])
        for ruta in rutas:
            ruta.en_uso = ruta.id in en_uso
        return rutas

    def get_by_id(self, ruta_id: int) -> Ruta | None:
        ruta = (
            self.db.query(Ruta)
            .options(joinedload(Ruta.peajes), joinedload(Ruta.puntos_carga))
            .filter(Ruta.id == ruta_id)
            .first()
        )
        if ruta:
            ruta.en_uso = ruta.id in self._ids_en_uso([ruta.id])
        return ruta