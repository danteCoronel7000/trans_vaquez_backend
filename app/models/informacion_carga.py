from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class InformacionCarga(Base):
    __tablename__ = "informacion_carga"

    id                = Column(Integer, primary_key=True, index=True)
    tipo              = Column(String(100), nullable=False)
    cantidad          = Column(Numeric(10, 2), nullable=False)
    peso_item         = Column(Numeric(10, 2), nullable=False)   # peso unitario
    volumen_item      = Column(Numeric(10, 2), nullable=False)   # volumen unitario
    peso              = Column(Numeric(10, 2), nullable=False)   # calculado: cantidad * peso_item
    volumen           = Column(Numeric(10, 2), nullable=False)   # calculado: cantidad * volumen_item
    id_servicio_cliente = Column(Integer, ForeignKey("servicio_cliente.id", ondelete="CASCADE"), nullable=False)

    servicio_cliente = relationship("ServicioCliente", back_populates="informaciones_carga")