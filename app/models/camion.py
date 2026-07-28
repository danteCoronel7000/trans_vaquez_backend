from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.database import Base


class Camion(Base):
    __tablename__ = "camiones"

    id                          = Column(Integer, primary_key=True, index=True)
    placa                       = Column(String(20),  unique=True, nullable=False)
    marca                       = Column(String(100), nullable=False)
    modelo                      = Column(String(100), nullable=False)
    color                       = Column(String(50),  nullable=False)
    capacidad_carga_kg          = Column(Float,       nullable=False)
    volumen_capacity_m3         = Column(Float,       nullable=False)
    anio                        = Column(Integer,     nullable=False)
    numero_chasis               = Column(String(100), unique=True, nullable=False)
    numero_motor                = Column(String(100), unique=True, nullable=False)
    vencimiento_soat            = Column(Date,        nullable=False)
    vencimiento_inspeccion_tecnica = Column(Date,     nullable=False)
    is_active                   = Column(Boolean,     default=True, nullable=False)
    created_at                  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at                  = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación 1:1 con Image
    image = relationship(
        "Image",
        back_populates="camion",
        uselist=False,
        cascade="all, delete-orphan"
    )
    servicios = relationship("ServicioMecanico", back_populates="camion", cascade="all, delete-orphan")