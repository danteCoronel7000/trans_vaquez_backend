from sqlalchemy import Column, Integer, String, Text, Boolean, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class TallerMecanico(Base):
    __tablename__ = "taller_mecanico"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(150), nullable=False)
    telefono    = Column(String(30),  nullable=True)
    direccion   = Column(String(200), nullable=True)
    ciudad      = Column(String(100), nullable=True)
    contacto    = Column(String(100), nullable=True)
    observacion = Column(Text,        nullable=True)
    is_active   = Column(Boolean, nullable=False, server_default=text("true"))  # 👈 nuevo

    servicios = relationship("ServicioMecanico", back_populates="taller")