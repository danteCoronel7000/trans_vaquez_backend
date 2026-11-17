from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.repositories.reporte_repository import ReporteRepository
from app.schemas.reportes import (
    FiltroReporteServicios, FilaReporteServicio,
    ReporteServiciosResponse, UbicacionGPSResumen
)
from app.schemas.reportes import (
    FilaServicioCliente, ResumenCliente, GrupoCliente,
    ReporteServiciosPorClienteResponse,
)

from app.schemas.reportes import (
    FilaViajeChofer, ResumenChofer, GrupoChofer, ReporteViajesPorChoferResponse,
)

def _f(value) -> float:
    """Convierte Decimal/None a float para poder mezclar con los campos Float del camión."""
    return float(value) if value is not None else 0.0

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

    def _resolver_fechas(self, filtro: FiltroReporteServicios):
        if filtro.tipo_periodo == "fecha_especifica":
            return filtro.fecha_inicio, filtro.fecha_inicio
        if filtro.tipo_periodo == "rango":
            return filtro.fecha_inicio, filtro.fecha_fin
        return None, None

    def _resumir(self, filas: list[FilaServicioCliente]) -> ResumenCliente:
        # Los servicios cancelados se listan pero no suman en los totales
        validas = [f for f in filas if f.estado != "cancelado"]

        peso     = sum(f.peso_carga for f in validas)
        volumen  = sum(f.volumen_carga for f in validas)
        costo    = sum(f.costo_cliente for f in validas)
        costo_op = sum(f.costo_operativo_prorrateado for f in validas)

        return ResumenCliente(
            total_servicios=len({f.id_servicio for f in validas}),
            servicios_cancelados=len({f.id_servicio for f in filas if f.estado == "cancelado"}),
            peso_total=round(peso, 2),
            volumen_total=round(volumen, 2),
            costo_total=round(costo, 2),
            costo_operativo_total=round(costo_op, 2),
            utilidad_total=round(costo - costo_op, 2),
            costo_promedio_por_kg=round(costo / peso, 2) if peso else None,
        )

    def generar_reporte_servicios_por_cliente(
        self, filtro: FiltroReporteServicios
    ) -> ReporteServiciosPorClienteResponse:
        self._validar_filtro(filtro)
        fecha_inicio, fecha_fin = self._resolver_fechas(filtro)
        servicios = self.repo.get_servicios_para_reporte(fecha_inicio, fecha_fin)

        grupos_dict: dict[int, dict] = {}

        for servicio in servicios:
            clientes_servicio = servicio.servicios_cliente
            if not clientes_servicio:
                continue

            costo_operativo_servicio = (
                _f(servicio.viaticos_chofer)
                + _f(servicio.viaticos_ayudante)
                + _f(servicio.combustible)
            )
            peso_total_servicio = sum(_f(sc.peso_total) for sc in clientes_servicio)
            capacidad_peso      = _f(servicio.camion.capacidad_carga_kg)
            capacidad_volumen   = _f(servicio.camion.volumen_capacity_m3)

            for sc in clientes_servicio:
                peso    = _f(sc.peso_total)
                volumen = _f(sc.volumen_total)
                costo   = _f(sc.costo_total)

                # Fracción del viaje que corresponde a este cliente (por peso).
                # Si el servicio no tiene peso registrado, se reparte en partes iguales.
                if peso_total_servicio > 0:
                    fraccion = peso / peso_total_servicio
                else:
                    fraccion = 1 / len(clientes_servicio)

                costo_op_prorrateado = costo_operativo_servicio * fraccion

                fila = FilaServicioCliente(
                    id_servicio=servicio.id,
                    fecha=servicio.fecha_creacion,
                    origen=servicio.punto_carga,
                    destino=servicio.punto_descarga,
                    camion=f"{servicio.camion.placa} - {servicio.camion.marca} {servicio.camion.modelo}",
                    chofer=f"{servicio.chofer.person.first_name} {servicio.chofer.person.last_name}",
                    estado=servicio.estado.value,
                    peso_carga=round(peso, 2),
                    volumen_carga=round(volumen, 2),
                    costo_cliente=round(costo, 2),
                    costo_por_kg=round(costo / peso, 2) if peso else None,
                    costo_por_m3=round(costo / volumen, 2) if volumen else None,
                    ocupacion_peso_pct=round(peso / capacidad_peso * 100, 2) if capacidad_peso else None,
                    ocupacion_volumen_pct=round(volumen / capacidad_volumen * 100, 2) if capacidad_volumen else None,
                    participacion_pct=round(fraccion * 100, 2),
                    costo_operativo_prorrateado=round(costo_op_prorrateado, 2),
                    utilidad_estimada=round(costo - costo_op_prorrateado, 2),
                )

                grupo = grupos_dict.setdefault(sc.id_cliente, {
                    "cliente": f"{sc.cliente.person.first_name} {sc.cliente.person.last_name}",
                    "razon_social": sc.cliente.razon_social,
                    "nit": sc.cliente.nit,
                    "filas": [],
                })
                grupo["filas"].append(fila)

        grupos = [
            GrupoCliente(
                id_cliente=id_cliente,
                cliente=datos["cliente"],
                razon_social=datos["razon_social"],
                nit=datos["nit"],
                filas=datos["filas"],
                resumen=self._resumir(datos["filas"]),
            )
            for id_cliente, datos in grupos_dict.items()
        ]
        grupos.sort(key=lambda g: g.cliente.lower())

        todas_las_filas = [f for g in grupos for f in g.filas]

        return ReporteServiciosPorClienteResponse(
            filtro_aplicado=filtro,
            total_clientes=len(grupos),
            grupos=grupos,
            resumen_general=self._resumir(todas_las_filas),
        )

    def _resumir_viajes(self, filas: list[FilaViajeChofer]) -> ResumenChofer:
            # Los viajes cancelados se listan pero no suman en los totales
            validas = [f for f in filas if f.estado != "cancelado"]
    
            return ResumenChofer(
                total_viajes=len(validas),
                viajes_programados=sum(1 for f in filas if f.estado == "programado"),
                viajes_en_curso=sum(1 for f in filas if f.estado == "en_curso"),
                viajes_finalizados=sum(1 for f in filas if f.estado == "finalizado"),
                viajes_cancelados=sum(1 for f in filas if f.estado == "cancelado"),
                km_total=round(sum(f.distancia_km or 0 for f in validas), 2),
                horas_estimadas_total=round(sum(f.tiempo_estimado_h or 0 for f in validas), 2),
                peso_total=round(sum(f.peso_transportado for f in validas), 2),
                volumen_total=round(sum(f.volumen_transportado for f in validas), 2),
                ingresos_total=round(sum(f.ingresos_viaje for f in validas), 2),
                costo_operativo_total=round(sum(f.costo_operativo for f in validas), 2),
                viaticos_chofer_total=round(sum(f.viaticos_chofer for f in validas), 2),
                utilidad_total=round(sum(f.utilidad_viaje for f in validas), 2),
            )

    def generar_reporte_viajes_por_chofer(
        self, filtro: FiltroReporteServicios
    ) -> ReporteViajesPorChoferResponse:
        self._validar_filtro(filtro)
        fecha_inicio, fecha_fin = self._resolver_fechas(filtro)

        servicios = self.repo.get_servicios_para_reporte(fecha_inicio, fecha_fin)
        rangos_gps = self.repo.get_rangos_gps([s.id for s in servicios])

        grupos_dict: dict[int, dict] = {}

        for servicio in servicios:
            clientes = servicio.servicios_cliente

            peso     = sum(_f(sc.peso_total) for sc in clientes)
            volumen  = sum(_f(sc.volumen_total) for sc in clientes)
            ingresos = sum(_f(sc.costo_total) for sc in clientes)

            viaticos_chofer = _f(servicio.viaticos_chofer)
            costo_operativo = (
                viaticos_chofer
                + _f(servicio.viaticos_ayudante)
                + _f(servicio.combustible)
            )

            distancia = servicio.ruta.distancia
            tiempo    = servicio.ruta.tiempo_estimado
            capacidad = _f(servicio.camion.capacidad_carga_kg)

            # Duración real: solo si hay al menos 2 puntos GPS registrados
            duracion_real = None
            rango = rangos_gps.get(servicio.id)
            if rango and rango[2] >= 2:
                duracion_real = round((rango[1] - rango[0]).total_seconds() / 3600, 2)

            fila = FilaViajeChofer(
                id_servicio=servicio.id,
                fecha=servicio.fecha_creacion,
                ruta=servicio.ruta.nombre,
                origen=servicio.punto_carga,
                destino=servicio.punto_descarga,
                camion=f"{servicio.camion.placa} - {servicio.camion.marca} {servicio.camion.modelo}",
                estado=servicio.estado.value,
                num_clientes=len(clientes),
                distancia_km=distancia,
                tiempo_estimado_h=tiempo,
                viaticos_chofer=round(viaticos_chofer, 2),
                peso_transportado=round(peso, 2),
                volumen_transportado=round(volumen, 2),
                ingresos_viaje=round(ingresos, 2),
                costo_operativo=round(costo_operativo, 2),
                utilidad_viaje=round(ingresos - costo_operativo, 2),
                ocupacion_peso_pct=round(peso / capacidad * 100, 2) if capacidad else None,
                costo_operativo_por_km=round(costo_operativo / distancia, 2) if distancia else None,
                velocidad_promedio_estimada=round(distancia / tiempo, 2) if distancia and tiempo else None,
                duracion_real_horas=duracion_real,
            )

            chofer = servicio.chofer
            grupo = grupos_dict.setdefault(servicio.id_chofer, {
                "chofer": f"{chofer.person.first_name} {chofer.person.last_name}",
                "licencia": chofer.licencia,
                "categoria": chofer.categoria.value if chofer.categoria else None,
                "filas": [],
            })
            grupo["filas"].append(fila)

        grupos = [
            GrupoChofer(
                id_chofer=id_chofer,
                chofer=datos["chofer"],
                licencia=datos["licencia"],
                categoria=datos["categoria"],
                filas=datos["filas"],
                resumen=self._resumir_viajes(datos["filas"]),
            )
            for id_chofer, datos in grupos_dict.items()
        ]
        grupos.sort(key=lambda g: g.chofer.lower())

        todas_las_filas = [f for g in grupos for f in g.filas]

        return ReporteViajesPorChoferResponse(
            filtro_aplicado=filtro,
            total_choferes=len(grupos),
            grupos=grupos,
            resumen_general=self._resumir_viajes(todas_las_filas),
        )