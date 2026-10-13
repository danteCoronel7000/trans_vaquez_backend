from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.schemas.reportes import FiltroReporteServicios, ReporteServiciosResponse
from app.services.reporte_service import ReporteService
from app.services.pdf_service import generar_pdf_reporte_servicios
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

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