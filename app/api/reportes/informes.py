from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.informes import FiltroInformeSemanal, FiltroInformeMensual, InformeResponse
from app.services.informe_service import InformeService

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> InformeService:
    return InformeService(db)


def _nombre_emisor(user: User) -> str:
    person = user.person
    return f"{person.first_name} {person.last_name}" if person else user.username


@router.post("/semanal", response_model=InformeResponse)
def generar_informe_semanal(
    filtro: FiltroInformeSemanal,
    svc: InformeService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.generar_semanal(filtro.fecha_referencia, _nombre_emisor(current_user))

@router.post("/mensual", response_model=InformeResponse)
def generar_informe_mensual(
    filtro: FiltroInformeMensual,
    svc: InformeService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.generar_mensual(filtro.anio, filtro.mes, _nombre_emisor(current_user))