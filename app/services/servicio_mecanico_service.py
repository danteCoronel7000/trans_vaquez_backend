from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.servicio_mecanico import ServicioMecanico
from app.models.detalle_repuesto import DetalleRepuesto
from app.repositories.servicio_mecanico_repository import ServicioMecanicoRepository
from app.repositories.detalle_repuesto_repository import DetalleRepuestoRepository
from app.repositories.camion_repository import CamionRepository
from app.repositories.taller_mecanico_repository import TallerMecanicoRepository
from app.repositories.tipo_servicio_repository import TipoServicioRepository
from app.repositories.repuesto_repository import RepuestoRepository
from app.schemas.servicio_mecanico import ServicioCreate, ServicioUpdate
from app.schemas.detalle_repuesto import DetalleCreate, DetalleUpdate
from app.exceptions.http_exceptions import NotFoundException


class ServicioMecanicoService:
    def __init__(self, db: Session):
        self.repo          = ServicioMecanicoRepository(db)
        self.detalle_repo  = DetalleRepuestoRepository(db)
        self.camion_repo   = CamionRepository(db)
        self.taller_repo   = TallerMecanicoRepository(db)
        self.tipo_repo     = TipoServicioRepository(db)
        self.repuesto_repo = RepuestoRepository(db)

    def _recalcular_totales(self, servicio: ServicioMecanico) -> None:
        subtotal = sum(d.subtotal for d in servicio.detalles)
        servicio.subtotal_repuestos = subtotal
        servicio.total = subtotal + servicio.mano_obra
        self.repo.db.commit()
        self.repo.db.refresh(servicio)

    def create(self, data: ServicioCreate) -> ServicioMecanico:
        if not self.camion_repo.get_by_id(data.camion_id):
            raise NotFoundException("Camión no encontrado")
        if not self.taller_repo.get_by_id(data.taller_id):
            raise NotFoundException("Taller mecánico no encontrado")
        if not self.tipo_repo.get_by_id(data.tipo_servicio_id):
            raise NotFoundException("Tipo de servicio no encontrado")

        servicio = ServicioMecanico(
            camion_id        = data.camion_id,
            taller_id        = data.taller_id,
            tipo_servicio_id = data.tipo_servicio_id,
            fecha            = data.fecha,
            kilometraje      = data.kilometraje,
            descripcion      = data.descripcion,
            mano_obra        = data.mano_obra,
            subtotal_repuestos = Decimal("0"),
            total            = data.mano_obra,
            observaciones    = data.observaciones,
        )
        return self.repo.create(servicio)

    def get_all(self, skip: int, limit: int) -> list[ServicioMecanico]:
        return self.repo.get_all(skip, limit)

    def get_by_camion(self, camion_id: int) -> list[ServicioMecanico]:
        return self.repo.get_by_camion(camion_id)

    def get_by_id(self, servicio_id: int) -> ServicioMecanico:
        servicio = self.repo.get_by_id(servicio_id)
        if not servicio:
            raise NotFoundException("Servicio mecánico no encontrado")
        return servicio

    def update(self, servicio_id: int, data: ServicioUpdate) -> ServicioMecanico:
        servicio = self.get_by_id(servicio_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(servicio, field, value)
        self.repo.db.commit()
        self.repo.db.refresh(servicio)
        self._recalcular_totales(servicio)
        return servicio

    def delete(self, servicio_id: int) -> None:
        servicio = self.get_by_id(servicio_id)
        self.repo.delete(servicio)

    # Detalle repuestos
    def add_detalle(self, servicio_id: int, data: DetalleCreate) -> ServicioMecanico:
        servicio = self.get_by_id(servicio_id)

        if not self.repuesto_repo.get_by_id(data.repuesto_id):
            raise NotFoundException("Repuesto no encontrado")

        subtotal = data.cantidad * data.precio_unitario
        detalle = DetalleRepuesto(
            mantenimiento_id = servicio_id,
            repuesto_id      = data.repuesto_id,
            cantidad         = data.cantidad,
            precio_unitario  = data.precio_unitario,
            subtotal         = subtotal,
        )
        self.detalle_repo.db.add(detalle)
        self.detalle_repo.db.commit()
        self.detalle_repo.db.refresh(detalle)
        self._recalcular_totales(servicio)
        return self.get_by_id(servicio_id)

    def update_detalle(
        self, servicio_id: int, detalle_id: int, data: DetalleUpdate
    ) -> ServicioMecanico:
        servicio = self.get_by_id(servicio_id)
        detalle = self.detalle_repo.get_by_id(detalle_id)
        if not detalle or detalle.mantenimiento_id != servicio_id:
            raise NotFoundException("Detalle de repuesto no encontrado")

        if data.cantidad is not None:
            detalle.cantidad = data.cantidad
        if data.precio_unitario is not None:
            detalle.precio_unitario = data.precio_unitario

        detalle.subtotal = detalle.cantidad * detalle.precio_unitario
        self.detalle_repo.db.commit()
        self._recalcular_totales(servicio)
        return self.get_by_id(servicio_id)

    def remove_detalle(self, servicio_id: int, detalle_id: int) -> ServicioMecanico:
        servicio = self.get_by_id(servicio_id)
        detalle = self.detalle_repo.get_by_id(detalle_id)
        if not detalle or detalle.mantenimiento_id != servicio_id:
            raise NotFoundException("Detalle de repuesto no encontrado")

        self.detalle_repo.db.delete(detalle)
        self.detalle_repo.db.commit()
        self._recalcular_totales(servicio)
        return self.get_by_id(servicio_id)