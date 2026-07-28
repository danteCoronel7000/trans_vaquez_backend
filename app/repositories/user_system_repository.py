from sqlalchemy.orm import Session
from app.models.user_system import UserSystem
from app.repositories.base import BaseRepository


class UserSystemRepository(BaseRepository[UserSystem]):
    def __init__(self, db: Session):
        super().__init__(UserSystem, db)

    def get_by_person_id(self, person_id: int) -> UserSystem | None:
        return self.db.query(UserSystem).filter(
            UserSystem.person_id == person_id
        ).first()