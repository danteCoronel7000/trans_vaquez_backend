from sqlalchemy import Column, Integer, String, Text, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ServicioMecanico(Base):
    __tablename__ = "servicio_mecanico"

    id                  = Column(Integer,     primary_key=True, index=True)
    camion_id           = Column(Integer,     ForeignKey("camiones.id", ondelete="CASCADE"), nullable=False)
    taller_id           = Column(Integer,     ForeignKey("taller_mecanico.id", ondelete="RESTRICT"), nullable=False)
    tipo_servicio_id    = Column(Integer,     ForeignKey("tipo_servicio.id",   ondelete="RESTRICT"), nullable=False)
    fecha               = Column(Date,        nullable=False)
    kilometraje         = Column(Integer,     nullable=True)
    descripcion         = Column(Text,        nullable=True)
    mano_obra           = Column(Numeric(10, 2), nullable=False, default=0)
    subtotal_repuestos  = Column(Numeric(10, 2), nullable=False, default=0)
    total               = Column(Numeric(10, 2), nullable=False, default=0)
    observaciones       = Column(Text,        nullable=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())

    camion        = relationship("Camion",        back_populates="servicios")
    taller        = relationship("TallerMecanico", back_populates="servicios")
    tipo_servicio = relationship("TipoServicio",   back_populates="servicios")
    detalles      = relationship("DetalleRepuesto", back_populates="servicio", cascade="all, delete-orphan")