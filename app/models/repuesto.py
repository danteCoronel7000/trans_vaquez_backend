from sqlalchemy import Column, Integer, String, Text, Boolean, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Repuesto(Base):
    __tablename__ = "repuestos"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(150), nullable=False)
    marca       = Column(String(100), nullable=True)
    unidad      = Column(String(30),  nullable=False)
    descripcion = Column(Text, nullable=True)
    is_active   = Column(Boolean, nullable=False, server_default=text("true"))
    detalles = relationship("DetalleRepuesto", back_populates="repuesto")