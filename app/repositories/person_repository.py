from sqlalchemy.orm import Session
from app.models.person import Person
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    def __init__(self, db: Session):
        super().__init__(Person, db)

    def get_by_user_id(self, user_id: int) -> Person | None:
        return self.db.query(Person).filter(Person.user_id == user_id).first()

    def get_by_ci(self, ci: str) -> Person | None:
        return self.db.query(Person).filter(Person.ci == ci).first()