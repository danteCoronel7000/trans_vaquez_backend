from sqlalchemy.orm import Session
from app.models.ubicacion_gps import UbicacionGPS
from app.repositories.base import BaseRepository


class UbicacionGPSRepository(BaseRepository[UbicacionGPS]):
    def __init__(self, db: Session):
        super().__init__(UbicacionGPS, db)

    def get_ultima(self, servicio_id: int) -> UbicacionGPS | None:
        return (
            self.db.query(UbicacionGPS)
            .filter(UbicacionGPS.id_servicio_transporte == servicio_id)
            .order_by(UbicacionGPS.fecha_hora.desc())
            .first()
        )

    def get_historial(self, servicio_id: int, limit: int = 500) -> list[UbicacionGPS]:
        return (
            self.db.query(UbicacionGPS)
            .filter(UbicacionGPS.id_servicio_transporte == servicio_id)
            .order_by(UbicacionGPS.fecha_hora.asc())
            .limit(limit)
            .all()
        )