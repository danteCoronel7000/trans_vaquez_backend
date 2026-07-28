from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DetalleRepuesto(Base):
    __tablename__ = "detalle_repuesto"

    id               = Column(Integer,      primary_key=True, index=True)
    mantenimiento_id = Column(Integer,      ForeignKey("servicio_mecanico.id", ondelete="CASCADE"), nullable=False)
    repuesto_id      = Column(Integer,      ForeignKey("repuestos.id",         ondelete="RESTRICT"), nullable=False)
    cantidad         = Column(Numeric(10, 2), nullable=False)
    precio_unitario  = Column(Numeric(10, 2), nullable=False)
    subtotal         = Column(Numeric(10, 2), nullable=False)

    servicio = relationship("ServicioMecanico", back_populates="detalles")
    repuesto = relationship("Repuesto",          back_populates="detalles")