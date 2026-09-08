from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.ubicacion_gps import UbicacionGPSCreate, UbicacionGPSOut
from app.services.ubicacion_gps_service import UbicacionGPSService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> UbicacionGPSService:
    return UbicacionGPSService(db)


@router.post(
    "/{servicio_id}/ubicaciones",
    response_model=UbicacionGPSOut,
    status_code=status.HTTP_201_CREATED,
)
def registrar_ubicacion(
    servicio_id: int,
    data: UbicacionGPSCreate,
    svc: UbicacionGPSService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.registrar_ubicacion(servicio_id, data, current_user)


@router.get("/{servicio_id}/ubicaciones/ultima", response_model=UbicacionGPSOut)
def get_ultima_ubicacion(
    servicio_id: int,
    svc: UbicacionGPSService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.get_ultima(servicio_id, current_user)


@router.get("/{servicio_id}/ubicaciones", response_model=list[UbicacionGPSOut])
def get_historial_ubicaciones(
    servicio_id: int,
    svc: UbicacionGPSService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return svc.get_historial(servicio_id, current_user)