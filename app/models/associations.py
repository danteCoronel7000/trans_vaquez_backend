from sqlalchemy import Table, Column, ForeignKey, Integer
from app.core.database import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_menus = Table(
    "role_menus",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_id", Integer, ForeignKey("menus.id", ondelete="CASCADE"), primary_key=True),
)

menu_processes = Table(
    "menu_processes",
    Base.metadata,
    Column("menu_id", Integer, ForeignKey("menus.id", ondelete="CASCADE"), primary_key=True),
    Column("process_id", Integer, ForeignKey("processes.id", ondelete="CASCADE"), primary_key=True),
)

ruta_peajes = Table(
    "ruta_peajes",
    Base.metadata,
    Column("ruta_id", Integer, ForeignKey("ruta.id", ondelete="CASCADE"), primary_key=True),
    Column("punto_peaje_id", Integer, ForeignKey("punto_peaje.id", ondelete="CASCADE"), primary_key=True),
)

ruta_puntos_carga = Table(
    "ruta_puntos_carga",
    Base.metadata,
    Column("ruta_id", Integer, ForeignKey("ruta.id", ondelete="CASCADE"), primary_key=True),
    Column("punto_carga_id", Integer, ForeignKey("punto_carga_combustible.id", ondelete="CASCADE"), primary_key=True),
)