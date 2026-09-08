from sqlalchemy.orm import Session, joinedload
from app.models.servicio_mecanico import ServicioMecanico
from app.models.detalle_repuesto import DetalleRepuesto
from app.repositories.base import BaseRepository


class ServicioMecanicoRepository(BaseRepository[ServicioMecanico]):
    def __init__(self, db: Session):
        super().__init__(ServicioMecanico, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ServicioMecanico]:
        return (
            self.db.query(ServicioMecanico)
            .options(
                joinedload(ServicioMecanico.taller),
                joinedload(ServicioMecanico.tipo_servicio),
                joinedload(ServicioMecanico.detalles).joinedload(DetalleRepuesto.repuesto),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, servicio_id: int) -> ServicioMecanico | None:
        return (
            self.db.query(ServicioMecanico)
            .options(
                joinedload(ServicioMecanico.taller),
                joinedload(ServicioMecanico.tipo_servicio),
                joinedload(ServicioMecanico.detalles).joinedload(DetalleRepuesto.repuesto),
            )
            .filter(ServicioMecanico.id == servicio_id)
            .first()
        )

    def get_by_camion(self, camion_id: int) -> list[ServicioMecanico]:
        return (
            self.db.query(ServicioMecanico)
            .options(
                joinedload(ServicioMecanico.taller),
                joinedload(ServicioMecanico.tipo_servicio),
                joinedload(ServicioMecanico.detalles).joinedload(DetalleRepuesto.repuesto),
            )
            .filter(ServicioMecanico.camion_id == camion_id)
            .all()
        )