from sqlalchemy import Column, Integer, String, Boolean, text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.associations import ruta_peajes


class PuntoPeaje(Base):
    __tablename__ = "punto_peaje"

    id           = Column(Integer, primary_key=True, index=True)
    nombre       = Column(String(50), nullable=False)
    departamento = Column(String(50), nullable=True)
    is_active    = Column(Boolean, nullable=False, server_default=text("true"))

    rutas = relationship(
        "Ruta",
        secondary=ruta_peajes,
        back_populates="peajes"
    )