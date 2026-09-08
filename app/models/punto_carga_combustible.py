from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.associations import ruta_puntos_carga


class PuntoCargaCombustible(Base):
    __tablename__ = "punto_carga_combustible"

    id           = Column(Integer, primary_key=True, index=True)
    nombre       = Column(String(50), nullable=False)
    direccion    = Column(String(100), nullable=True)
    ciudad       = Column(String(50), nullable=True)
    departamento = Column(String(50), nullable=True)
    is_active    = Column(Boolean, default=True, nullable=False)

    rutas = relationship(
        "Ruta",
        secondary=ruta_puntos_carga,
        back_populates="puntos_carga"
    )