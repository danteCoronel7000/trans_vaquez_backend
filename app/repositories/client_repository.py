from sqlalchemy.orm import Session, joinedload
from app.models.client import Client
from app.repositories.base import BaseRepository


class ClientRepository(BaseRepository[Client]):
    def __init__(self, db: Session):
        super().__init__(Client, db)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Client]:
        return (
            self.db.query(Client)
            .options(joinedload(Client.person))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, client_id: int) -> Client | None:
        return (
            self.db.query(Client)
            .options(joinedload(Client.person))
            .filter(Client.id == client_id)
            .first()
        )

    def get_by_person_id(self, person_id: int) -> Client | None:
        return self.db.query(Client).filter(Client.person_id == person_id).first()