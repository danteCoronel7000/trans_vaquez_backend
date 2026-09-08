from sqlalchemy.orm import Session
from app.models.user_system import UserSystem
from app.repositories.user_system_repository import UserSystemRepository
from app.repositories.user_repository import UserRepository
from app.exceptions.http_exceptions import NotFoundException


class UserSystemService:
    def __init__(self, db: Session):
        self.repo      = UserSystemRepository(db)
        self.user_repo = UserRepository(db)

    def get_by_user_id(self, user_id: int) -> UserSystem:
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.person:
            raise NotFoundException("El usuario no tiene una persona asociada")

        user_system = self.repo.get_by_person_id(user.person.id)
        if not user_system:
            raise NotFoundException("Este usuario no tiene un registro de usuario_sistema (no tiene rol administrativo)")

        return user_system