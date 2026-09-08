from sqlalchemy.orm import Session
from app.models.ubicacion_gps import UbicacionGPS
from app.models.servicio_transporte import EstadoServicioEnum, ServicioTransporte
from app.models.user import User
from app.repositories.ubicacion_gps_repository import UbicacionGPSRepository
from app.repositories.servicio_transporte_repository import ServicioTransporteRepository
from app.schemas.ubicacion_gps import UbicacionGPSCreate
from app.exceptions.http_exceptions import NotFoundException, ConflictException, ForbiddenException

# Roles considerados "administrativos" (reutiliza el mismo criterio que usamos en user_service)
ROLES_ADMINISTRATIVOS = {"ADMIN", "ENCARGADO", "DUEÑO"}


class UbicacionGPSService:
    def __init__(self, db: Session):
        self.repo         = UbicacionGPSRepository(db)
        self.servicio_repo = ServicioTransporteRepository(db)

    def _get_servicio(self, servicio_id: int):
        servicio = self.servicio_repo.get_by_id(servicio_id)
        if not servicio:
            raise NotFoundException("Servicio de transporte no encontrado")
        return servicio

    def registrar_ubicacion(
        self, servicio_id: int, data: UbicacionGPSCreate, current_user: User
    ) -> UbicacionGPS:
        servicio = self._get_servicio(servicio_id)

        # Validar que el servicio esté en curso
        if servicio.estado != EstadoServicioEnum.EN_CURSO:
            raise ConflictException(
                "Solo se puede registrar ubicación cuando el servicio está 'en_curso'"
            )

        # Validar que quien envía es el chofer asignado a este servicio
        if not current_user.person or not current_user.person.chofer:
            raise ForbiddenException("El usuario no está asociado a un chofer")

        if current_user.person.chofer.id != servicio.id_chofer:
            raise ForbiddenException("No estás asignado como chofer de este servicio")

        ubicacion = UbicacionGPS(
            id_servicio_transporte = servicio_id,
            latitud    = data.latitud,
            longitud   = data.longitud,
            velocidad  = data.velocidad,
        )
        return self.repo.create(ubicacion)

    def _validar_acceso_consulta(self, servicio: ServicioTransporte, current_user: User) -> None:
        roles_usuario = {r.name.upper() for r in current_user.roles}
        if roles_usuario.intersection(ROLES_ADMINISTRATIVOS):
            return
    
        # Permitir también al cliente dueño de una carga en este servicio específico
        if current_user.person and current_user.person.client:
            cliente_id = current_user.person.client.id
            if any(sc.id_cliente == cliente_id for sc in servicio.servicios_cliente):
                return
    
        raise ForbiddenException("No tienes permisos para consultar el seguimiento de este servicio")


    def get_ultima(self, servicio_id: int, current_user: User) -> UbicacionGPS:
        servicio = self._get_servicio(servicio_id)
        self._validar_acceso_consulta(servicio, current_user)
    
        ultima = self.repo.get_ultima(servicio_id)
        if not ultima:
            raise NotFoundException("Aún no hay ubicaciones registradas para este servicio")
        return ultima

    def get_historial(self, servicio_id: int, current_user: User) -> list[UbicacionGPS]:
        servicio = self._get_servicio(servicio_id)
        self._validar_acceso_consulta(servicio, current_user)
        return self.repo.get_historial(servicio_id)