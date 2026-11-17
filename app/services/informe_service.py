import math
from collections import defaultdict
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.models.servicio_transporte import ServicioTransporte, EstadoServicioEnum
from app.repositories.reporte_repository import ReporteRepository
from app.schemas.informes import (
    Periodo, ResumenEjecutivo, IndicadorComparado, ItemCosto, DesgloseCostos,
    ActividadDia, DetalleServicio, FilaFlota, ResumenFlota, FilaRutaDestino,
    RutasDestinos, ServicioBasico, IncidenciaCancelado, Incidencias,
    AlertaDocumento, TopCliente, ProductividadChofer, AgendaServicio,
    AgendaProxima, FilaDistanciaGPS, DistanciaGPS, InformeResponse,
)

DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DIAS_ALERTA_DOCUMENTOS = 30    # se alerta cuando faltan 30 días o menos para vencer
UMBRAL_GPS_KM = 0.01           # ignora saltos < 10 m (ruido del GPS con el camión detenido)

CANCELADO = EstadoServicioEnum.CANCELADO


# ── Helpers de cálculo ────────────────────────────────────
def _f(valor) -> float:
    return float(valor) if valor is not None else 0.0


def _pct(parte: float, total: float, decimales: int = 2) -> float | None:
    return round(parte / total * 100, decimales) if total else None


def _variacion(actual: float, anterior: float) -> float | None:
    if anterior == 0:
        return None
    return round((actual - anterior) / anterior * 100, 2)


def _haversine_km(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def _peso(s: ServicioTransporte) -> float:
    return sum(_f(sc.peso_total) for sc in s.servicios_cliente)


def _volumen(s: ServicioTransporte) -> float:
    return sum(_f(sc.volumen_total) for sc in s.servicios_cliente)


def _ingresos(s: ServicioTransporte) -> float:
    return sum(_f(sc.costo_total) for sc in s.servicios_cliente)


def _costo_operativo(s: ServicioTransporte) -> float:
    return _f(s.viaticos_chofer) + _f(s.viaticos_ayudante) + _f(s.combustible)


def _nombre_persona(person) -> str:
    return f"{person.first_name} {person.last_name}"


def _nombre_camion(camion) -> str:
    return f"{camion.placa} - {camion.marca} {camion.modelo}"


def _nombre_chofer(s: ServicioTransporte) -> str:
    return _nombre_persona(s.chofer.person)


def _clientes(s: ServicioTransporte) -> str:
    nombres = [_nombre_persona(sc.cliente.person) for sc in s.servicios_cliente]
    return ", ".join(nombres) if nombres else "Sin clientes"


class InformeService:
    def __init__(self, db: Session):
        self.repo = ReporteRepository(db)

    # ── Puntos de entrada ─────────────────────────────────
    @staticmethod
    def rango_semana(fecha_ref: date) -> tuple[date, date]:
        lunes = fecha_ref - timedelta(days=fecha_ref.weekday())
        return lunes, lunes + timedelta(days=6)

    def generar_semanal(self, fecha_ref: date, emitido_por: str) -> InformeResponse:
        inicio, fin = self.rango_semana(fecha_ref)
        return self._generar(
            tipo="semanal",
            inicio=inicio, fin=fin,
            ant_ini=inicio - timedelta(days=7), ant_fin=fin - timedelta(days=7),
            sig_ini=inicio + timedelta(days=7), sig_fin=fin + timedelta(days=7),
            emitido_por=emitido_por,
        )

    # ── Motor común (lo reutilizará el informe mensual) ───
    def _generar(
        self, tipo: str,
        inicio: date, fin: date,
        ant_ini: date, ant_fin: date,
        sig_ini: date, sig_fin: date,
        emitido_por: str,
    ) -> InformeResponse:
        servicios      = self.repo.get_servicios_para_reporte(inicio, fin)
        servicios_ant  = self.repo.get_servicios_para_reporte(ant_ini, ant_fin)
        mantenimientos     = self.repo.get_mantenimientos(inicio, fin)
        mantenimientos_ant = self.repo.get_mantenimientos(ant_ini, ant_fin)
        camiones = self.repo.get_camiones_activos()

        validos = [s for s in servicios if s.estado != CANCELADO]

        resumen     = self._resumen(servicios, sum(_f(m.total) for m in mantenimientos))
        resumen_ant = self._resumen(servicios_ant, sum(_f(m.total) for m in mantenimientos_ant))

        return InformeResponse(
            tipo=tipo,
            periodo=Periodo(inicio=inicio, fin=fin),
            periodo_anterior=Periodo(inicio=ant_ini, fin=ant_fin),
            emitido_por=emitido_por,
            emitido_en=datetime.now().astimezone(),
            resumen=resumen,
            comparativo=self._comparativo(resumen, resumen_ant),
            costos=self._costos(resumen, validos),
            actividad_diaria=self._actividad_diaria(inicio, fin, servicios),
            servicios=self._detalle(servicios),
            flota=self._flota(validos, mantenimientos, camiones),
            rutas_destinos=self._rutas_destinos(validos),
            incidencias=self._incidencias(servicios),
            alertas=self._alertas(camiones, date.today()),
            top_clientes=self._top_clientes(validos),
            choferes=self._choferes(validos),
            agenda=self._agenda(sig_ini, sig_fin),
            distancia_gps=self._distancia_gps(validos),
        )

    # ── 2. Resumen ejecutivo ──────────────────────────────
    def _resumen(self, servicios: list[ServicioTransporte], costo_mantenimiento: float) -> ResumenEjecutivo:
        validos    = [s for s in servicios if s.estado != CANCELADO]
        cancelados = len(servicios) - len(validos)

        ingresos       = sum(_ingresos(s) for s in validos)
        costo_op       = sum(_costo_operativo(s) for s in validos)
        utilidad_bruta = ingresos - costo_op
        utilidad_neta  = utilidad_bruta - costo_mantenimiento

        return ResumenEjecutivo(
            total_servicios=len(servicios),
            programados=sum(1 for s in servicios if s.estado == EstadoServicioEnum.PROGRAMADO),
            en_curso=sum(1 for s in servicios if s.estado == EstadoServicioEnum.EN_CURSO),
            finalizados=sum(1 for s in servicios if s.estado == EstadoServicioEnum.FINALIZADO),
            cancelados=cancelados,
            tasa_cancelacion_pct=_pct(cancelados, len(servicios)),
            peso_total_kg=round(sum(_peso(s) for s in validos), 2),
            volumen_total_m3=round(sum(_volumen(s) for s in validos), 2),
            ingresos=round(ingresos, 2),
            costo_operativo=round(costo_op, 2),
            costo_mantenimiento=round(costo_mantenimiento, 2),
            utilidad_bruta=round(utilidad_bruta, 2),
            utilidad_neta=round(utilidad_neta, 2),
            margen_pct=_pct(utilidad_neta, ingresos),
        )

    # ── 3. Comparativo con el período anterior ────────────
    def _comparativo(self, actual: ResumenEjecutivo, anterior: ResumenEjecutivo) -> list[IndicadorComparado]:
        def ind(nombre: str, unidad: str, a: float, b: float, mejor_si_sube: bool = True):
            return IndicadorComparado(
                nombre=nombre, unidad=unidad, actual=a, anterior=b,
                variacion_pct=_variacion(a, b), mejor_si_sube=mejor_si_sube,
            )

        return [
            ind("Servicios", "", actual.total_servicios, anterior.total_servicios),
            ind("Carga transportada", "kg", actual.peso_total_kg, anterior.peso_total_kg),
            ind("Ingresos", "Bs.", actual.ingresos, anterior.ingresos),
            ind("Costo operativo", "Bs.", actual.costo_operativo, anterior.costo_operativo, mejor_si_sube=False),
            ind("Utilidad neta", "Bs.", actual.utilidad_neta, anterior.utilidad_neta),
        ]

    # ── 4. Desglose de costos ─────────────────────────────
    def _costos(self, resumen: ResumenEjecutivo, validos: list[ServicioTransporte]) -> DesgloseCostos:
        combustible = sum(_f(s.combustible) for s in validos)
        v_chofer    = sum(_f(s.viaticos_chofer) for s in validos)
        v_ayudante  = sum(_f(s.viaticos_ayudante) for s in validos)
        mant        = resumen.costo_mantenimiento
        total       = combustible + v_chofer + v_ayudante + mant

        items = [
            ItemCosto(concepto=concepto, monto=round(monto, 2), porcentaje=_pct(monto, total))
            for concepto, monto in (
                ("Combustible", combustible),
                ("Viáticos de chofer", v_chofer),
                ("Viáticos de ayudante", v_ayudante),
                ("Mantenimiento mecánico", mant),
            )
        ]
        return DesgloseCostos(
            items=items,
            total_costos=round(total, 2),
            ingresos=resumen.ingresos,
            utilidad_neta=resumen.utilidad_neta,
        )

    # ── 5. Actividad diaria ───────────────────────────────
    def _actividad_diaria(self, inicio: date, fin: date, servicios: list[ServicioTransporte]) -> list[ActividadDia]:
        por_dia: dict[date, list[ServicioTransporte]] = defaultdict(list)
        for s in servicios:
            por_dia[s.fecha_creacion.date()].append(s)

        dias: list[ActividadDia] = []
        dia = inicio
        while dia <= fin:
            lista   = por_dia.get(dia, [])
            validos = [s for s in lista if s.estado != CANCELADO]
            dias.append(ActividadDia(
                fecha=dia,
                dia_semana=DIAS_SEMANA[dia.weekday()],
                servicios=len(validos),
                cancelados=len(lista) - len(validos),
                peso_kg=round(sum(_peso(s) for s in validos), 2),
                ingresos=round(sum(_ingresos(s) for s in validos), 2),
            ))
            dia += timedelta(days=1)
        return dias

    # ── 6. Detalle de servicios ───────────────────────────
    def _detalle(self, servicios: list[ServicioTransporte]) -> list[DetalleServicio]:
        return [
            DetalleServicio(
                id_servicio=s.id,
                fecha=s.fecha_creacion,
                ruta=s.ruta.nombre,
                clientes=_clientes(s),
                camion=_nombre_camion(s.camion),
                chofer=_nombre_chofer(s),
                estado=s.estado.value,
                peso_kg=round(_peso(s), 2),
                volumen_m3=round(_volumen(s), 2),
                ingresos=round(_ingresos(s), 2),
                costo_operativo=round(_costo_operativo(s), 2),
            )
            for s in sorted(servicios, key=lambda x: x.fecha_creacion)
        ]

    # ── 7. Flota ──────────────────────────────────────────
    def _flota(self, validos: list[ServicioTransporte], mantenimientos, camiones) -> ResumenFlota:
        info: dict[int, dict] = {}

        for c in camiones:
            info[c.id] = {"camion": c, "activo": True, "servicios": []}
        for s in validos:
            info.setdefault(
                s.id_camion, {"camion": s.camion, "activo": s.camion.is_active, "servicios": []}
            )["servicios"].append(s)

        mant_por_camion: dict[int, list] = defaultdict(list)
        for m in mantenimientos:
            mant_por_camion[m.camion_id].append(m)
            info.setdefault(
                m.camion_id, {"camion": m.camion, "activo": m.camion.is_active, "servicios": []}
            )

        filas: list[FilaFlota] = []
        for camion_id, d in info.items():
            camion    = d["camion"]
            lista     = d["servicios"]
            capacidad = _f(camion.capacidad_carga_kg)
            ocupaciones = [_peso(s) / capacidad * 100 for s in lista] if capacidad else []
            mants = mant_por_camion.get(camion_id, [])

            filas.append(FilaFlota(
                id_camion=camion_id,
                camion=_nombre_camion(camion),
                viajes=len(lista),
                km=round(sum(s.ruta.distancia or 0 for s in lista), 2),
                peso_kg=round(sum(_peso(s) for s in lista), 2),
                ocupacion_promedio_pct=round(sum(ocupaciones) / len(ocupaciones), 2) if ocupaciones else None,
                mantenimientos=len(mants),
                costo_mantenimiento=round(sum(_f(m.total) for m in mants), 2),
                sin_actividad=len(lista) == 0,
            ))

        filas.sort(key=lambda f: (f.sin_actividad, -f.viajes, f.camion))

        activos_total   = len(camiones)
        activos_con_act = sum(1 for d in info.values() if d["activo"] and d["servicios"])

        return ResumenFlota(
            camiones_activos=activos_total,
            camiones_con_actividad=activos_con_act,
            camiones_sin_actividad=activos_total - activos_con_act,
            utilizacion_pct=_pct(activos_con_act, activos_total),
            filas=filas,
        )

    # ── 8. Rutas y destinos ───────────────────────────────
    def _rutas_destinos(self, validos: list[ServicioTransporte]) -> RutasDestinos:
        por_ruta: dict = {}
        por_destino: dict = {}

        def acumular(dic: dict, clave, nombre: str, detalle: str | None, s: ServicioTransporte) -> None:
            d = dic.setdefault(clave, {
                "nombre": nombre, "detalle": detalle,
                "servicios": 0, "peso": 0.0, "ingresos": 0.0,
            })
            d["servicios"] += 1
            d["peso"]      += _peso(s)
            d["ingresos"]  += _ingresos(s)

        for s in validos:
            r = s.ruta
            acumular(por_ruta, r.id, r.nombre, f"{r.ciudad_origen} → {r.ciudad_destino}", s)
            destino = r.ciudad_destino.strip()
            acumular(por_destino, destino.lower(), destino, None, s)

        def a_filas(dic: dict) -> list[FilaRutaDestino]:
            filas = [
                FilaRutaDestino(
                    nombre=d["nombre"], detalle=d["detalle"], servicios=d["servicios"],
                    peso_kg=round(d["peso"], 2), ingresos=round(d["ingresos"], 2),
                )
                for d in dic.values()
            ]
            filas.sort(key=lambda f: (-f.servicios, -f.ingresos))
            return filas

        return RutasDestinos(por_ruta=a_filas(por_ruta), por_destino=a_filas(por_destino))

    # ── 9. Incidencias ────────────────────────────────────
    def _incidencias(self, servicios: list[ServicioTransporte]) -> Incidencias:
        def basico(s: ServicioTransporte) -> dict:
            return dict(
                id_servicio=s.id, fecha=s.fecha_creacion, ruta=s.ruta.nombre,
                camion=_nombre_camion(s.camion), chofer=_nombre_chofer(s),
            )

        return Incidencias(
            cancelados=[
                IncidenciaCancelado(**basico(s), motivo=s.motivo_cancelacion)
                for s in servicios if s.estado == CANCELADO
            ],
            en_curso=[
                ServicioBasico(**basico(s))
                for s in servicios if s.estado == EstadoServicioEnum.EN_CURSO
            ],
        )

    # ── 10. Alertas de cumplimiento ───────────────────────
    def _alertas(self, camiones, hoy: date) -> list[AlertaDocumento]:
        alertas: list[AlertaDocumento] = []
        for c in camiones:
            for documento, vencimiento in (
                ("SOAT", c.vencimiento_soat),
                ("Inspección técnica", c.vencimiento_inspeccion_tecnica),
            ):
                if not vencimiento:
                    continue
                dias = (vencimiento - hoy).days
                if dias <= DIAS_ALERTA_DOCUMENTOS:
                    alertas.append(AlertaDocumento(
                        camion=_nombre_camion(c),
                        documento=documento,
                        fecha_vencimiento=vencimiento,
                        dias_restantes=dias,
                        nivel="vencido" if dias < 0 else "por_vencer",
                    ))
        alertas.sort(key=lambda a: a.dias_restantes)
        return alertas

    # ── 11. Top clientes ──────────────────────────────────
    def _top_clientes(self, validos: list[ServicioTransporte], limite: int = 10) -> list[TopCliente]:
        acum: dict[int, dict] = {}
        for s in validos:
            for sc in s.servicios_cliente:
                d = acum.setdefault(sc.id_cliente, {
                    "cliente": _nombre_persona(sc.cliente.person),
                    "servicios": set(), "peso": 0.0, "ingresos": 0.0,
                })
                d["servicios"].add(s.id)
                d["peso"]     += _f(sc.peso_total)
                d["ingresos"] += _f(sc.costo_total)

        filas = [
            TopCliente(
                cliente=d["cliente"], servicios=len(d["servicios"]),
                peso_kg=round(d["peso"], 2), ingresos=round(d["ingresos"], 2),
            )
            for d in acum.values()
        ]
        filas.sort(key=lambda f: -f.ingresos)
        return filas[:limite]

    # ── 12. Productividad por chofer ──────────────────────
    def _choferes(self, validos: list[ServicioTransporte]) -> list[ProductividadChofer]:
        acum: dict[int, dict] = {}
        for s in validos:
            d = acum.setdefault(s.id_chofer, {
                "chofer": _nombre_chofer(s),
                "viajes": 0, "km": 0.0, "horas": 0.0, "peso": 0.0, "viaticos": 0.0,
            })
            d["viajes"]   += 1
            d["km"]       += s.ruta.distancia or 0
            d["horas"]    += s.ruta.tiempo_estimado or 0
            d["peso"]     += _peso(s)
            d["viaticos"] += _f(s.viaticos_chofer)

        filas = [
            ProductividadChofer(
                chofer=d["chofer"], viajes=d["viajes"], km=round(d["km"], 2),
                horas_estimadas=round(d["horas"], 2), peso_kg=round(d["peso"], 2),
                viaticos=round(d["viaticos"], 2),
            )
            for d in acum.values()
        ]
        filas.sort(key=lambda f: (-f.viajes, f.chofer))
        return filas

    # ── 13. Agenda del próximo período ────────────────────
    def _agenda(self, sig_ini: date, sig_fin: date) -> AgendaProxima:
        programados = self.repo.get_programados_entre(sig_ini, sig_fin)
        return AgendaProxima(
            inicio=sig_ini,
            fin=sig_fin,
            servicios=[
                AgendaServicio(
                    id_servicio=s.id,
                    fecha_salida=s.fecha_salida_programada,
                    ruta=s.ruta.nombre,
                    clientes=_clientes(s),
                    camion=_nombre_camion(s.camion),
                    chofer=_nombre_chofer(s),
                )
                for s in programados
            ],
            programados_sin_fecha=self.repo.contar_programados_sin_fecha(),
        )

    # ── 14. Distancia real recorrida por GPS ──────────────
    def _distancia_gps(self, validos: list[ServicioTransporte]) -> DistanciaGPS:
        puntos = self.repo.get_puntos_gps([s.id for s in validos])

        filas: list[FilaDistanciaGPS] = []
        for s in validos:
            pts = puntos.get(s.id, [])
            if len(pts) < 2:
                continue

            tramos = (_haversine_km(a, b) for a, b in zip(pts, pts[1:]))
            km_gps = sum(t for t in tramos if t >= UMBRAL_GPS_KM)
            plan   = s.ruta.distancia

            filas.append(FilaDistanciaGPS(
                id_servicio=s.id,
                ruta=s.ruta.nombre,
                camion=_nombre_camion(s.camion),
                km_planificados=plan,
                km_gps=round(km_gps, 2),
                diferencia_pct=round((km_gps - plan) / plan * 100, 2) if plan else None,
            ))

        return DistanciaGPS(
            servicios_con_gps=len(filas),
            km_gps_total=round(sum(f.km_gps for f in filas), 2),
            filas=filas,
        )