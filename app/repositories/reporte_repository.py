from datetime import date, datetime, time
from sqlalchemy.orm import Session, joinedload
from app.models.servicio_transporte import ServicioTransporte, EstadoServicioEnum
from app.models.servicio_cliente import ServicioCliente
from app.models.ubicacion_gps import UbicacionGPS
from sqlalchemy import func
from app.models.servicio_mecanico import ServicioMecanico
from app.models.camion import Camion


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

    def get_rangos_gps(self, servicio_ids: list[int]) -> dict[int, tuple[datetime, datetime, int]]:
        """Primer punto, último punto y cantidad de puntos GPS por servicio (una sola consulta)."""
        if not servicio_ids:
            return {}

        filas = (
            self.db.query(
                UbicacionGPS.id_servicio_transporte,
                func.min(UbicacionGPS.fecha_hora),
                func.max(UbicacionGPS.fecha_hora),
                func.count(UbicacionGPS.id),
            )
            .filter(UbicacionGPS.id_servicio_transporte.in_(servicio_ids))
            .group_by(UbicacionGPS.id_servicio_transporte)
            .all()
        )
        return {f[0]: (f[1], f[2], f[3]) for f in filas}

    def get_camiones_activos(self) -> list[Camion]:
        return self.db.query(Camion).filter(Camion.is_active.is_(True)).all()

    def get_mantenimientos(self, inicio: date, fin: date) -> list[ServicioMecanico]:
        return (
            self.db.query(ServicioMecanico)
            .filter(ServicioMecanico.fecha >= inicio, ServicioMecanico.fecha <= fin)
            .all()
        )

    def get_programados_entre(self, inicio: date, fin: date) -> list[ServicioTransporte]:
        """Servicios programados cuya salida cae dentro del rango (para la agenda)."""
        return (
            self.db.query(ServicioTransporte)
            .options(
                joinedload(ServicioTransporte.ruta),
                joinedload(ServicioTransporte.chofer),
                joinedload(ServicioTransporte.camion),
                joinedload(ServicioTransporte.servicios_cliente)
                    .joinedload(ServicioCliente.cliente),
            )
            .filter(
                ServicioTransporte.estado == EstadoServicioEnum.PROGRAMADO,
                ServicioTransporte.fecha_salida_programada >= datetime.combine(inicio, time.min),
                ServicioTransporte.fecha_salida_programada <= datetime.combine(fin, time.max),
            )
            .order_by(ServicioTransporte.fecha_salida_programada.asc())
            .all()
        )

    def contar_programados_sin_fecha(self) -> int:
        return (
            self.db.query(func.count(ServicioTransporte.id))
            .filter(
                ServicioTransporte.estado == EstadoServicioEnum.PROGRAMADO,
                ServicioTransporte.fecha_salida_programada.is_(None),
            )
            .scalar()
        ) or 0

    def get_puntos_gps(self, servicio_ids: list[int]) -> dict[int, list[tuple[float, float]]]:
        """Puntos (lat, lon) ordenados cronológicamente, agrupados por servicio. Una sola consulta."""
        if not servicio_ids:
            return {}

        filas = (
            self.db.query(
                UbicacionGPS.id_servicio_transporte,
                UbicacionGPS.latitud,
                UbicacionGPS.longitud,
            )
            .filter(UbicacionGPS.id_servicio_transporte.in_(servicio_ids))
            .order_by(UbicacionGPS.id_servicio_transporte, UbicacionGPS.fecha_hora)
            .all()
        )

        puntos: dict[int, list[tuple[float, float]]] = {}
        for servicio_id, lat, lon in filas:
            puntos.setdefault(servicio_id, []).append((lat, lon))
        return puntos