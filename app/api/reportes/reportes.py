from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.schemas.reportes import FiltroReporteServicios, ReporteServiciosResponse
from app.services.reporte_service import ReporteService
from app.services.pdf_service import generar_pdf_reporte_servicios
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

from app.schemas.reportes import (
    FiltroReporteServicios, ReporteServiciosResponse,
    ReporteServiciosPorClienteResponse,
)
from app.services.pdf_service import (
    generar_pdf_reporte_servicios,
    generar_pdf_reporte_servicios_por_cliente,
)
from app.schemas.reportes import ReporteViajesPorChoferResponse
from app.services.pdf_service import generar_pdf_reporte_viajes_por_chofer

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> ReporteService:
    return ReporteService(db)


@router.post("/servicios-transporte", response_model=ReporteServiciosResponse)
def generar_reporte_servicios(
    filtro: FiltroReporteServicios,
    svc: ReporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.generar_reporte_servicios(filtro)


@router.post("/servicios-transporte/pdf")
def generar_reporte_servicios_pdf(
    filtro: FiltroReporteServicios,
    svc: ReporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    reporte = svc.generar_reporte_servicios(filtro)
    pdf_bytes = generar_pdf_reporte_servicios(reporte)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte_servicios_transporte.pdf"}
    )

@router.post("/servicios-por-cliente", response_model=ReporteServiciosPorClienteResponse)
def generar_reporte_servicios_por_cliente(
    filtro: FiltroReporteServicios,
    svc: ReporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.generar_reporte_servicios_por_cliente(filtro)


@router.post("/servicios-por-cliente/pdf")
def generar_reporte_servicios_por_cliente_pdf(
    filtro: FiltroReporteServicios,
    svc: ReporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    reporte = svc.generar_reporte_servicios_por_cliente(filtro)
    pdf_bytes = generar_pdf_reporte_servicios_por_cliente(reporte)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte_servicios_por_cliente.pdf"},
    )

@router.post("/viajes-por-chofer", response_model=ReporteViajesPorChoferResponse)
def generar_reporte_viajes_por_chofer(
    filtro: FiltroReporteServicios,
    svc: ReporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    return svc.generar_reporte_viajes_por_chofer(filtro)


@router.post("/viajes-por-chofer/pdf")
def generar_reporte_viajes_por_chofer_pdf(
    filtro: FiltroReporteServicios,
    svc: ReporteService = Depends(get_service),
    _=Depends(get_current_user),
):
    reporte = svc.generar_reporte_viajes_por_chofer(filtro)
    pdf_bytes = generar_pdf_reporte_viajes_por_chofer(reporte)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte_viajes_por_chofer.pdf"},
    )