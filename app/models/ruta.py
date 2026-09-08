from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.associations import ruta_peajes, ruta_puntos_carga


class Ruta(Base):
    __tablename__ = "ruta"

    id               = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(50), nullable=False)
    ciudad_origen    = Column(String(50), nullable=False)
    ciudad_destino   = Column(String(50), nullable=False)
    distancia        = Column(Float, nullable=True)   # en km
    tiempo_estimado  = Column(Float, nullable=True)   # en horas
    tipo_de_via      = Column(String(50), nullable=True)
    is_active        = Column(Boolean, default=True, nullable=False)

    peajes = relationship(
        "PuntoPeaje",
        secondary=ruta_peajes,
        back_populates="rutas"
    )
    puntos_carga = relationship(
        "PuntoCargaCombustible",
        secondary=ruta_puntos_carga,
        back_populates="rutas"
    )