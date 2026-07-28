from sqlalchemy.orm import Session, joinedload
from app.models.chofer import Chofer
from app.repositories.base import BaseRepository


class ChoferRepository(BaseRepository[Chofer]):
    def __init__(self, db: Session):
        super().__init__(Chofer, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Chofer]:
        return (
            self.db.query(Chofer)
            .options(joinedload(Chofer.person))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, chofer_id: int) -> Chofer | None:
        return (
            self.db.query(Chofer)
            .options(joinedload(Chofer.person))
            .filter(Chofer.id == chofer_id)
            .first()
        )

    def get_by_person_id(self, person_id: int) -> Chofer | None:
        return self.db.query(Chofer).filter(Chofer.person_id == person_id).first()

    def get_by_licencia(self, licencia: str) -> Chofer | None:
        return self.db.query(Chofer).filter(Chofer.licencia == licencia).first()