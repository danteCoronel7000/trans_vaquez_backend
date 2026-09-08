from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.user_system import UserSystemOut
from app.services.user_system_service import UserSystemService
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> UserSystemService:
    return UserSystemService(db)


@router.get("/me", response_model=UserSystemOut)
def get_my_user_system(
    svc: UserSystemService = Depends(get_service),
    current_user=Depends(get_current_user),
):
    return svc.get_by_user_id(current_user.id)