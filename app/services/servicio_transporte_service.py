from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.servicio_transporte import ServicioTransporte, EstadoServicioEnum
from app.models.servicio_cliente import ServicioCliente
from app.models.informacion_carga import InformacionCarga
from app.models.user import User
from app.repositories.servicio_transporte_repository import ServicioTransporteRepository
from app.repositories.servicio_cliente_repository import ServicioClienteRepository
from app.repositories.informacion_carga_repository import InformacionCargaRepository
from app.repositories.camion_repository import CamionRepository
from app.repositories.chofer_repository import ChoferRepository
from app.repositories.client_repository import ClientRepository
from app.repositories.ruta_repository import RutaRepository
from app.schemas.ruta import RutaOut
from app.schemas.servicio_transporte import CamionResumenOut, ChoferResumenOut, MiCargaOut, ServicioTransporteClienteOut, ServicioTransporteCreate, ServicioTransporteUpdate
from app.schemas.servicio_cliente import ServicioClienteCreate, ServicioClienteUpdate
from app.schemas.informacion_carga import InformacionCargaCreate, InformacionCargaUpdate
from app.exceptions.http_exceptions import ForbiddenException, NotFoundException, ConflictException


# Transiciones válidas de estado
TRANSICIONES_VALIDAS = {
    EstadoServicioEnum.PROGRAMADO: {EstadoServicioEnum.EN_CURSO, EstadoServicioEnum.CANCELADO},
    EstadoServicioEnum.EN_CURSO:   {EstadoServicioEnum.FINALIZADO, EstadoServicioEnum.CANCELADO},
    EstadoServicioEnum.FINALIZADO: set(),
    EstadoServicioEnum.CANCELADO:  set(),
}

ROLES_ADMINISTRATIVOS = {"ADMIN", "ENCARGADO", "DUEÑO"}

class ServicioTransporteService:
    def __init__(self, db: Session):
        self.repo             = ServicioTransporteRepository(db)
        self.sc_repo          = ServicioClienteRepository(db)
        self.carga_repo       = InformacionCargaRepository(db)
        self.camion_repo      = CamionRepository(db)
        self.chofer_repo      = ChoferRepository(db)
        self.client_repo      = ClientRepository(db)
        self.ruta_repo        = RutaRepository(db)

    # ── Validaciones de creación ──────────────────────────────
    def _validar_recursos(self, camion_id: int, chofer_id: int, ruta_id: int, excluir_id: int | None = None) -> None:
        camion = self.camion_repo.get_by_id(camion_id)
        if not camion:
            raise NotFoundException("Camión no encontrado")
        if not camion.is_active:
            raise ConflictException("El camión no está habilitado")

        chofer = self.chofer_repo.get_by_id(chofer_id)
        if not chofer:
            raise NotFoundException("Chofer no encontrado")
        if not chofer.is_active:
            raise ConflictException("El chofer no está habilitado")

        ruta = self.ruta_repo.get_by_id(ruta_id)
        if not ruta:
            raise NotFoundException("Ruta no encontrada")
        if not ruta.is_active:
            raise ConflictException("La ruta no está habilitada")

        if self.repo.camion_en_servicio_activo(camion_id, excluir_id):
            raise ConflictException("El camión ya está asignado a otro servicio activo (programado/en curso)")

        if self.repo.chofer_en_servicio_activo(chofer_id, excluir_id):
            raise ConflictException("El chofer ya está asignado a otro servicio activo (programado/en curso)")

    # ── CRUD servicio_transporte ──────────────────────────────
    def create(self, data: ServicioTransporteCreate) -> ServicioTransporte:
        self._validar_recursos(data.id_camion, data.id_chofer, data.id_ruta)
    
        # Separar servicios_cliente del payload principal
        servicios_cliente_data = data.servicios_cliente
        servicio_dict = data.model_dump(exclude={"servicios_cliente"})
    
        servicio = ServicioTransporte(**servicio_dict)
        self.repo.db.add(servicio)
        self.repo.db.flush()  # para obtener servicio.id sin commitear aún
    
        for sc_data in servicios_cliente_data:
            # Validar cliente
            cliente = self.client_repo.get_by_id(sc_data.id_cliente)
            if not cliente:
                self.repo.db.rollback()
                raise NotFoundException(f"Cliente con id {sc_data.id_cliente} no encontrado")
            if not cliente.is_active:
                self.repo.db.rollback()
                raise ConflictException(f"El cliente {sc_data.id_cliente} no está habilitado")
    
            sc = ServicioCliente(
                id_servicio_transporte = servicio.id,
                id_cliente              = sc_data.id_cliente,
                costo_total              = sc_data.costo_total,
                peso_total               = Decimal("0"),
                volumen_total            = Decimal("0"),
            )
            self.sc_repo.db.add(sc)
            self.sc_repo.db.flush()  # obtener sc.id
    
            peso_acum    = Decimal("0")
            volumen_acum = Decimal("0")
    
            for carga_data in sc_data.informaciones_carga:
                peso    = carga_data.cantidad * carga_data.peso_item
                volumen = carga_data.cantidad * carga_data.volumen_item
    
                carga = InformacionCarga(
                    tipo                 = carga_data.tipo,
                    cantidad             = carga_data.cantidad,
                    peso_item            = carga_data.peso_item,
                    volumen_item         = carga_data.volumen_item,
                    peso                 = peso,
                    volumen              = volumen,
                    id_servicio_cliente  = sc.id,
                )
                self.carga_repo.db.add(carga)
    
                peso_acum    += peso
                volumen_acum += volumen
    
            sc.peso_total    = peso_acum
            sc.volumen_total = volumen_acum
    
        self.repo.db.commit()
        self.repo.db.refresh(servicio)
        return self.get_by_id(servicio.id)

    def get_all(self, skip: int, limit: int) -> list[ServicioTransporte]:
        return self.repo.get_all(skip, limit)

    def search(self, q: str, skip: int, limit: int) -> list[ServicioTransporte]:
        return self.repo.search(q, skip, limit)

    def get_by_id(self, servicio_id: int) -> ServicioTransporte:
        servicio = self.repo.get_by_id(servicio_id)
        if not servicio:
            raise NotFoundException("Servicio de transporte no encontrado")
        return servicio

    def _validar_editable(self, servicio: ServicioTransporte) -> None:
        if servicio.estado != EstadoServicioEnum.PROGRAMADO:
            raise ConflictException("Solo se pueden modificar servicios en estado 'programado'")

    def update(self, servicio_id: int, data: ServicioTransporteUpdate) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_editable(servicio)

        # Si cambia camión/chofer/ruta, revalidar
        nuevo_camion = data.id_camion if data.id_camion is not None else servicio.id_camion
        nuevo_chofer = data.id_chofer if data.id_chofer is not None else servicio.id_chofer
        nueva_ruta   = data.id_ruta   if data.id_ruta   is not None else servicio.id_ruta

        if data.id_camion or data.id_chofer or data.id_ruta:
            self._validar_recursos(nuevo_camion, nuevo_chofer, nueva_ruta, excluir_id=servicio_id)

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(servicio, field, value)

        return self.repo.update(servicio)

    # ── Transiciones de estado ────────────────────────────────
    def _cambiar_estado(self, servicio_id: int, nuevo_estado: EstadoServicioEnum) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)

        permitidos = TRANSICIONES_VALIDAS.get(servicio.estado, set())
        if nuevo_estado not in permitidos:
            raise ConflictException(
                f"No se puede cambiar de '{servicio.estado.value}' a '{nuevo_estado.value}'"
            )

        servicio.estado = nuevo_estado
        return self.repo.update(servicio)

    def _validar_permiso_transicion(self, servicio: ServicioTransporte, current_user: User) -> None:
        """
        Permite operar sobre el servicio a:
        - Un usuario administrativo (ADMIN, ENCARGADO, DUEÑO) — puede operar sobre cualquier servicio.
        - El chofer asignado a ESE servicio en particular.
        """
        roles_usuario = {r.name.upper() for r in current_user.roles}
        if roles_usuario.intersection(ROLES_ADMINISTRATIVOS):
            return  # es admin, se le permite sin más validación

        if not current_user.person or not current_user.person.chofer:
            raise ForbiddenException("El usuario no está asociado a un chofer")
        if current_user.person.chofer.id != servicio.id_chofer:
            raise ForbiddenException("No estás asignado como chofer de este servicio")

    def iniciar(self, servicio_id: int, current_user: User) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_permiso_transicion(servicio, current_user)

        if servicio.estado != EstadoServicioEnum.PROGRAMADO:
            raise ConflictException(
                f"No se puede iniciar un servicio en estado '{servicio.estado.value}'"
            )
        return self._cambiar_estado(servicio_id, EstadoServicioEnum.EN_CURSO)

    def finalizar(self, servicio_id: int, current_user: User) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_permiso_transicion(servicio, current_user)

        if servicio.estado != EstadoServicioEnum.EN_CURSO:
            raise ConflictException(
                f"No se puede finalizar un servicio en estado '{servicio.estado.value}'"
            )
        if not servicio.servicios_cliente:
            raise ConflictException("No se puede finalizar un servicio sin clientes/carga registrada")

        return self._cambiar_estado(servicio_id, EstadoServicioEnum.FINALIZADO)

    def cancelar(self, servicio_id: int, motivo: str, current_user: User) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_permiso_transicion(servicio, current_user)

        if servicio.estado == EstadoServicioEnum.FINALIZADO:
            raise ConflictException("No se puede anular un servicio finalizado")
        if not motivo or not motivo.strip():
            raise ConflictException("Debe indicar el motivo de la anulación")

        servicio = self._cambiar_estado(servicio_id, EstadoServicioEnum.CANCELADO)
        servicio.motivo_cancelacion = motivo.strip()
        self.repo.db.commit()
        self.repo.db.refresh(servicio)
        return servicio
    
    # ── Gestión de servicio_cliente ───────────────────────────
    def _validar_estado_editable_carga(self, servicio: ServicioTransporte) -> None:
        if servicio.estado != EstadoServicioEnum.PROGRAMADO:
            raise ConflictException("Solo se pueden agregar/quitar clientes en estado 'programado'")

    def add_cliente(self, servicio_id: int, data: ServicioClienteCreate) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_estado_editable_carga(servicio)

        cliente = self.client_repo.get_by_id(data.id_cliente)
        if not cliente:
            raise NotFoundException("Cliente no encontrado")
        if not cliente.is_active:
            raise ConflictException("El cliente no está habilitado")

        ya_existe = any(sc.id_cliente == data.id_cliente for sc in servicio.servicios_cliente)
        if ya_existe:
            raise ConflictException("El cliente ya está registrado en este servicio")

        sc = ServicioCliente(
            id_servicio_transporte = servicio_id,
            id_cliente              = data.id_cliente,
            costo_total              = data.costo_total,
            peso_total               = Decimal("0"),
            volumen_total            = Decimal("0"),
        )
        self.sc_repo.db.add(sc)
        self.sc_repo.db.commit()
        self.sc_repo.db.refresh(sc)
        return self.get_by_id(servicio_id)

    def update_cliente(self, servicio_id: int, sc_id: int, data: ServicioClienteUpdate) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_estado_editable_carga(servicio)

        sc = self.sc_repo.get_by_id(sc_id)
        if not sc or sc.id_servicio_transporte != servicio_id:
            raise NotFoundException("Registro de cliente no encontrado en este servicio")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(sc, field, value)
        self.sc_repo.db.commit()
        return self.get_by_id(servicio_id)

    def remove_cliente(self, servicio_id: int, sc_id: int) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_estado_editable_carga(servicio)

        sc = self.sc_repo.get_by_id(sc_id)
        if not sc or sc.id_servicio_transporte != servicio_id:
            raise NotFoundException("Registro de cliente no encontrado en este servicio")

        self.sc_repo.db.delete(sc)
        self.sc_repo.db.commit()
        return self.get_by_id(servicio_id)

    # ── Gestión de informacion_carga ──────────────────────────
    def _recalcular_totales_cliente(self, sc: ServicioCliente) -> None:
        peso_total    = sum(c.peso    for c in sc.informaciones_carga)
        volumen_total = sum(c.volumen for c in sc.informaciones_carga)
        sc.peso_total    = peso_total
        sc.volumen_total = volumen_total
        self.sc_repo.db.commit()
        self.sc_repo.db.refresh(sc)

    def add_carga(self, servicio_id: int, sc_id: int, data: InformacionCargaCreate) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_estado_editable_carga(servicio)

        sc = self.sc_repo.get_by_id(sc_id)
        if not sc or sc.id_servicio_transporte != servicio_id:
            raise NotFoundException("Registro de cliente no encontrado en este servicio")

        peso    = data.cantidad * data.peso_item
        volumen = data.cantidad * data.volumen_item

        carga = InformacionCarga(
            tipo                 = data.tipo,
            cantidad             = data.cantidad,
            peso_item            = data.peso_item,
            volumen_item         = data.volumen_item,
            peso                 = peso,
            volumen              = volumen,
            id_servicio_cliente  = sc_id,
        )
        self.carga_repo.db.add(carga)
        self.carga_repo.db.commit()
        self.carga_repo.db.refresh(carga)

        sc = self.sc_repo.get_by_id(sc_id)
        self._recalcular_totales_cliente(sc)
        return self.get_by_id(servicio_id)

    def update_carga(self, servicio_id: int, sc_id: int, carga_id: int, data: InformacionCargaUpdate) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_estado_editable_carga(servicio)

        carga = self.carga_repo.get_by_id(carga_id)
        if not carga or carga.id_servicio_cliente != sc_id:
            raise NotFoundException("Línea de carga no encontrada")

        for field, value in data.model_dump(exclude_none=True).items():
            setattr(carga, field, value)

        carga.peso    = carga.cantidad * carga.peso_item
        carga.volumen = carga.cantidad * carga.volumen_item
        self.carga_repo.db.commit()

        sc = self.sc_repo.get_by_id(sc_id)
        self._recalcular_totales_cliente(sc)
        return self.get_by_id(servicio_id)

    def remove_carga(self, servicio_id: int, sc_id: int, carga_id: int) -> ServicioTransporte:
        servicio = self.get_by_id(servicio_id)
        self._validar_estado_editable_carga(servicio)

        carga = self.carga_repo.get_by_id(carga_id)
        if not carga or carga.id_servicio_cliente != sc_id:
            raise NotFoundException("Línea de carga no encontrada")

        self.carga_repo.db.delete(carga)
        self.carga_repo.db.commit()

        sc = self.sc_repo.get_by_id(sc_id)
        self._recalcular_totales_cliente(sc)
        return self.get_by_id(servicio_id)

    def get_activo_por_usuario(self, current_user) -> ServicioTransporte:
        if not current_user.person or not current_user.person.chofer:
            raise NotFoundException("El usuario no está asociado a un chofer")
    
        chofer_id = current_user.person.chofer.id
        servicio = self.repo.get_activo_por_chofer(chofer_id)
    
        if not servicio:
            raise NotFoundException("No tienes un servicio de transporte activo en este momento")
    
        return servicio

    def _construir_respuesta_cliente(
            self, servicio: ServicioTransporte, mi_servicio_cliente: ServicioCliente
        ) -> ServicioTransporteClienteOut:
            return ServicioTransporteClienteOut(
                id=servicio.id,
                estado=servicio.estado,
                punto_carga=servicio.punto_carga,
                punto_descarga=servicio.punto_descarga,
                fecha_creacion=servicio.fecha_creacion,
                motivo_cancelacion=servicio.motivo_cancelacion,
                ruta=RutaOut.model_validate(servicio.ruta),
                chofer=ChoferResumenOut.model_validate(servicio.chofer),
                camion=CamionResumenOut.model_validate(servicio.camion),
                mi_carga=MiCargaOut.model_validate(mi_servicio_cliente),
            )

    def get_mis_servicios(self, current_user: User) -> list[ServicioTransporteClienteOut]:
        if not current_user.person or not current_user.person.client:
            raise ForbiddenException("El usuario no está asociado a un cliente")
    
        cliente_id = current_user.person.client.id
        servicios = self.repo.get_by_cliente(cliente_id)
    
        resultado = []
        for servicio in servicios:
            mi_carga = next(sc for sc in servicio.servicios_cliente if sc.id_cliente == cliente_id)
            resultado.append(self._construir_respuesta_cliente(servicio, mi_carga))
        return resultado