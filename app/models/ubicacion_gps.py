from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UbicacionGPS(Base):
    __tablename__ = "ubicacion_gps"

    id                      = Column(Integer, primary_key=True, index=True)
    id_servicio_transporte  = Column(
        Integer,
        ForeignKey("servicio_transporte.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    latitud     = Column(Float, nullable=False)
    longitud    = Column(Float, nullable=False)
    velocidad   = Column(Float, nullable=True)  # km/h, opcional
    fecha_hora  = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    servicio_transporte = relationship("ServicioTransporte")