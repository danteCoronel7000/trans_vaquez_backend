from sqlalchemy.orm import Session
from app.models.person import Person
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    def __init__(self, db: Session):
        super().__init__(Person, db)

    def get_by_ci(self, ci: str) -> Person | None:
        return self.db.query(Person).filter(Person.ci == ci).first()