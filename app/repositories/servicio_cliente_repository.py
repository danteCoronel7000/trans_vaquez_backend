from sqlalchemy.orm import Session, joinedload
from app.models.servicio_cliente import ServicioCliente
from app.repositories.base import BaseRepository


class ServicioClienteRepository(BaseRepository[ServicioCliente]):
    def __init__(self, db: Session):
        super().__init__(ServicioCliente, db)

    def get_by_id(self, sc_id: int) -> ServicioCliente | None:
        return (
            self.db.query(ServicioCliente)
            .options(joinedload(ServicioCliente.informaciones_carga))
            .filter(ServicioCliente.id == sc_id)
            .first()
        )