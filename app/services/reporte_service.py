from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.repositories.reporte_repository import ReporteRepository
from app.schemas.reportes import (
    FiltroReporteServicios, FilaReporteServicio,
    ReporteServiciosResponse, UbicacionGPSResumen
)
from app.exceptions.http_exceptions import ConflictException


class ReporteService:
    def __init__(self, db: Session):
        self.repo = ReporteRepository(db)

    def _validar_filtro(self, filtro: FiltroReporteServicios) -> None:
        if filtro.tipo_periodo == "fecha_especifica":
            if not filtro.fecha_inicio:
                raise ConflictException("Debe indicar la fecha específica")
        elif filtro.tipo_periodo == "rango":
            if not filtro.fecha_inicio or not filtro.fecha_fin:
                raise ConflictException("Debe indicar fecha de inicio y fecha de fin")
            if filtro.fecha_inicio > filtro.fecha_fin:
                raise ConflictException("La fecha de inicio no puede ser mayor a la fecha de fin")
        elif filtro.tipo_periodo != "todos":
            raise ConflictException("Tipo de período inválido")

    def generar_reporte_servicios(self, filtro: FiltroReporteServicios) -> ReporteServiciosResponse:
        self._validar_filtro(filtro)

        fecha_inicio = None
        fecha_fin = None

        if filtro.tipo_periodo == "fecha_especifica":
            fecha_inicio = filtro.fecha_inicio
            fecha_fin = filtro.fecha_inicio
        elif filtro.tipo_periodo == "rango":
            fecha_inicio = filtro.fecha_inicio
            fecha_fin = filtro.fecha_fin

        servicios = self.repo.get_servicios_para_reporte(fecha_inicio, fecha_fin)

        filas: list[FilaReporteServicio] = []

        for servicio in servicios:
            num_clientes = len(servicio.servicios_cliente)

            ultima_ubicacion = None
            if servicio.estado.value == "en_curso":
                ubicacion = self.repo.get_ultima_ubicacion(servicio.id)
                if ubicacion:
                    ultima_ubicacion = UbicacionGPSResumen(
                        latitud=ubicacion.latitud,
                        longitud=ubicacion.longitud,
                        fecha_hora=ubicacion.fecha_hora,
                    )

            if num_clientes == 0:
                # Servicio sin clientes asignados aún: igual aparece, con datos vacíos
                filas.append(FilaReporteServicio(
                    id_servicio=servicio.id,
                    cliente="Sin clientes asignados",
                    origen=servicio.punto_carga,
                    destino=servicio.punto_descarga,
                    camion=f"{servicio.camion.placa} - {servicio.camion.marca} {servicio.camion.modelo}",
                    chofer=f"{servicio.chofer.person.first_name} {servicio.chofer.person.last_name}",
                    fecha=servicio.fecha_creacion,
                    estado=servicio.estado.value,
                    peso_carga=Decimal("0"),
                    volumen_carga=Decimal("0"),
                    costo_cliente=Decimal("0"),
                    distancia_ruta=servicio.ruta.distancia,
                    tiempo_estimado_ruta=servicio.ruta.tiempo_estimado,
                    ultima_ubicacion=ultima_ubicacion,
                    num_clientes_servicio=0,
                ))
                continue

            for sc in servicio.servicios_cliente:
                nombre_cliente = f"{sc.cliente.person.first_name} {sc.cliente.person.last_name}"

                filas.append(FilaReporteServicio(
                    id_servicio=servicio.id,
                    cliente=nombre_cliente,
                    origen=servicio.punto_carga,
                    destino=servicio.punto_descarga,
                    camion=f"{servicio.camion.placa} - {servicio.camion.marca} {servicio.camion.modelo}",
                    chofer=f"{servicio.chofer.person.first_name} {servicio.chofer.person.last_name}",
                    fecha=servicio.fecha_creacion,
                    estado=servicio.estado.value,
                    peso_carga=sc.peso_total,
                    volumen_carga=sc.volumen_total,
                    costo_cliente=sc.costo_total,
                    distancia_ruta=servicio.ruta.distancia,
                    tiempo_estimado_ruta=servicio.ruta.tiempo_estimado,
                    ultima_ubicacion=ultima_ubicacion,
                    num_clientes_servicio=num_clientes,
                ))

        return ReporteServiciosResponse(
            filtro_aplicado=filtro,
            total_filas=len(filas),
            filas=filas,
        )