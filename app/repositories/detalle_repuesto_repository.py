from sqlalchemy.orm import Session
from app.models.detalle_repuesto import DetalleRepuesto
from app.repositories.base import BaseRepository


class DetalleRepuestoRepository(BaseRepository[DetalleRepuesto]):
    def __init__(self, db: Session):
        super().__init__(DetalleRepuesto, db)