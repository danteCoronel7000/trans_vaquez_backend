from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from app.schemas.role import RoleOut


class UserCreate(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id:         int
    username:   str
    is_active:  bool
    created_at: datetime
    roles:      list[RoleOut] = []  # ✅ agregar

    model_config = {"from_attributes": True}


class UserWithRoles(UserOut):
    roles: list["RoleOut"] = []


from app.schemas.role import RoleOut  # noqa: E402
UserWithRoles.model_rebuild()

class UserCreateWithPerson(BaseModel):
    username:   str
    password:   str
    id_persona: int

# ── Nuevo schema ──────────────────────────────────────
from typing import Optional
class UserListOut(BaseModel):
    id:         int
    username:   str
    email:      str
    is_active:  bool
    created_at: datetime
    roles:      list[RoleOut] = []

    # Datos de la persona — opcionales porque
    # un usuario puede no tener persona asignada
    gmail:      Optional[str] = None  # ← viene de la persona
    first_name: Optional[str] = None
    last_name:  Optional[str] = None
    ci:         Optional[str] = None

    model_config = {"from_attributes": True}


    @classmethod
    def from_user(cls, user) -> "UserListOut":
        # Extraemos los datos de la persona si existe
        person = getattr(user, "person", None)
        return cls(
            id         = user.id,
            username   = user.username,
            is_active  = user.is_active,
            created_at = user.created_at,
            roles      = user.roles,
            first_name = person.first_name if person else None,
            last_name  = person.last_name  if person else None,
            ci         = person.ci         if person else None,
            gmail      = person.gmail      if person else None,
        )
    
    # schemas/user.py  (y lo mismo en schemas/person.py)
class ToggleActiveOut(BaseModel):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)