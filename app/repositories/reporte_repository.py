from datetime import date, datetime, time
from sqlalchemy.orm import Session, joinedload
from app.models.servicio_transporte import ServicioTransporte
from app.models.servicio_cliente import ServicioCliente
from app.models.ubicacion_gps import UbicacionGPS


class ReporteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_servicios_para_reporte(
        self,
        fecha_inicio: date | None = None,
        fecha_fin: date | None = None,
    ) -> list[ServicioTransporte]:
        query = (
            self.db.query(ServicioTransporte)
            .options(
                joinedload(ServicioTransporte.ruta),
                joinedload(ServicioTransporte.chofer),
                joinedload(ServicioTransporte.camion),
                joinedload(ServicioTransporte.servicios_cliente)
                    .joinedload(ServicioCliente.cliente),
            )
        )

        if fecha_inicio:
            query = query.filter(
                ServicioTransporte.fecha_creacion >= datetime.combine(fecha_inicio, time.min)
            )
        if fecha_fin:
            query = query.filter(
                ServicioTransporte.fecha_creacion <= datetime.combine(fecha_fin, time.max)
            )

        return query.order_by(ServicioTransporte.fecha_creacion.desc()).all()

    def get_ultima_ubicacion(self, servicio_id: int) -> UbicacionGPS | None:
        return (
            self.db.query(UbicacionGPS)
            .filter(UbicacionGPS.id_servicio_transporte == servicio_id)
            .order_by(UbicacionGPS.fecha_hora.desc())
            .first()
        )