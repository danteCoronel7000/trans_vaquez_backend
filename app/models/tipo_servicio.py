from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipoServicio(Base):
    __tablename__ = "tipo_servicio"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)

    servicios = relationship("ServicioMecanico", back_populates="tipo_servicio")