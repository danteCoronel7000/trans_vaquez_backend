from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role
from app.repositories.base import BaseRepository
from sqlalchemy.orm import joinedload
from app.models.person import Person


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

        # En UserRepository
    def get_person_by_user_id(self, user_id: int) -> Person | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        return user.person if user else None
    
    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

        # ── Nuevo método ──────────────────────────────────
    def get_all_with_persons(
        self, skip: int = 0, limit: int = 100
    ) -> list[User]:
        # joinedload trae la persona y los roles
        # en la misma consulta, evitando el problema N+1
        return (
            self.db.query(User)
            .options(
                joinedload(User.person),  # trae la persona
                joinedload(User.roles),   # trae los roles
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def assign_role(self, user: User, role: Role) -> User:
        if role not in user.roles:
            user.roles.append(role)
            self.db.commit()
            self.db.refresh(user)
        return user

    def remove_role(self, user: User, role: Role) -> User:
        if role in user.roles:
            user.roles.remove(role)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    # repositories/user_repository.py

    def toggle_active(self, user_id: int) -> User:
        user = self.get_by_id(user_id)  # ya existe en BaseRepository
        user.is_active = not user.is_active
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_username_with_person(self, username: str) -> User | None:
        return (
            self.db.query(User)
            .options(
                joinedload(User.person).joinedload(Person.image)
            )
            .filter(User.username == username)
            .first()
        )