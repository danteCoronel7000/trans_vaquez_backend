from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ServicioCliente(Base):
    __tablename__ = "servicio_cliente"

    id                     = Column(Integer, primary_key=True, index=True)
    id_servicio_transporte = Column(Integer, ForeignKey("servicio_transporte.id", ondelete="CASCADE"), nullable=False)
    id_cliente             = Column(Integer, ForeignKey("clients.id",             ondelete="RESTRICT"), nullable=False)

    peso_total   = Column(Numeric(10, 2), nullable=False, default=0)
    volumen_total = Column(Numeric(10, 2), nullable=False, default=0)
    costo_total  = Column(Numeric(10, 2), nullable=False, default=0)

    servicio_transporte = relationship("ServicioTransporte", back_populates="servicios_cliente")
    cliente             = relationship("Client")

    informaciones_carga = relationship(
        "InformacionCarga",
        back_populates="servicio_cliente",
        cascade="all, delete-orphan"
    )