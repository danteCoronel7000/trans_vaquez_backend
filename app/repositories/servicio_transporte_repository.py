from sqlalchemy.orm import Session, joinedload
from app.models.servicio_transporte import ServicioTransporte, EstadoServicioEnum
from app.models.servicio_cliente import ServicioCliente
from app.repositories.base import BaseRepository


class ServicioTransporteRepository(BaseRepository[ServicioTransporte]):
    def __init__(self, db: Session):
        super().__init__(ServicioTransporte, db)

    def _base_query(self):
        return (
            self.db.query(ServicioTransporte)
            .options(
                joinedload(ServicioTransporte.ruta),
                joinedload(ServicioTransporte.chofer),
                joinedload(ServicioTransporte.camion),
                joinedload(ServicioTransporte.servicios_cliente)
                    .joinedload(ServicioCliente.informaciones_carga),  # ✅ atributo de clase, no string
            )
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ServicioTransporte]:
        return self._base_query().offset(skip).limit(limit).all()

    def get_by_id(self, servicio_id: int) -> ServicioTransporte | None:
        return self._base_query().filter(ServicioTransporte.id == servicio_id).first()

    def search(self, q: str, skip: int = 0, limit: int = 100) -> list[ServicioTransporte]:
        like = f"%{q}%"
        return (
            self._base_query()
            .filter(
                (ServicioTransporte.punto_carga.ilike(like)) |
                (ServicioTransporte.punto_descarga.ilike(like))
            )
            .offset(skip).limit(limit).all()
        )

    def camion_en_servicio_activo(self, camion_id: int, excluir_id: int | None = None) -> bool:
        q = self.db.query(ServicioTransporte).filter(
            ServicioTransporte.id_camion == camion_id,
            ServicioTransporte.estado.in_([EstadoServicioEnum.PROGRAMADO, EstadoServicioEnum.EN_CURSO])
        )
        if excluir_id:
            q = q.filter(ServicioTransporte.id != excluir_id)
        return self.db.query(q.exists()).scalar()

    def chofer_en_servicio_activo(self, chofer_id: int, excluir_id: int | None = None) -> bool:
        q = self.db.query(ServicioTransporte).filter(
            ServicioTransporte.id_chofer == chofer_id,
            ServicioTransporte.estado.in_([EstadoServicioEnum.PROGRAMADO, EstadoServicioEnum.EN_CURSO])
        )
        if excluir_id:
            q = q.filter(ServicioTransporte.id != excluir_id)
        return self.db.query(q.exists()).scalar()

    def get_activo_por_chofer(self, chofer_id: int) -> ServicioTransporte | None:
        return (
            self._base_query()
            .filter(
                ServicioTransporte.id_chofer == chofer_id,
                ServicioTransporte.estado.in_([EstadoServicioEnum.PROGRAMADO, EstadoServicioEnum.EN_CURSO])
            )
            .order_by(ServicioTransporte.fecha_creacion.desc())
            .first()
        )

    def get_by_cliente(self, cliente_id: int) -> list[ServicioTransporte]:
        return (
            self.db.query(ServicioTransporte)
            .join(ServicioTransporte.servicios_cliente)
            .filter(ServicioCliente.id_cliente == cliente_id)
            .order_by(ServicioTransporte.fecha_creacion.desc())
            .all()
        )