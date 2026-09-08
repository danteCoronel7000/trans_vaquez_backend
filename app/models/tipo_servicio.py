from sqlalchemy import Column, Integer, String, Text, Boolean, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class TipoServicio(Base):
    __tablename__ = "tipo_servicio"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    is_active   = Column(Boolean, nullable=False, server_default=text("true"))

    servicios = relationship("ServicioMecanico", back_populates="tipo_servicio")