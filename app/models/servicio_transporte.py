from sqlalchemy import Column, Integer, String, Numeric, Enum as SAEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class EstadoServicioEnum(str, enum.Enum):
    PROGRAMADO = "programado"
    EN_CURSO   = "en_curso"
    FINALIZADO = "finalizado"
    CANCELADO  = "cancelado"


class ServicioTransporte(Base):
    __tablename__ = "servicio_transporte"

    id                  = Column(Integer, primary_key=True, index=True)
    punto_carga         = Column(String(255), nullable=False)
    punto_descarga      = Column(String(255), nullable=False)
    viaticos_chofer     = Column(Numeric(10, 2), nullable=True, default=0)
    viaticos_ayudante   = Column(Numeric(10, 2), nullable=True, default=0)
    combustible         = Column(Numeric(10, 2), nullable=True, default=0)
    estado              = Column(SAEnum(EstadoServicioEnum), nullable=False, default=EstadoServicioEnum.PROGRAMADO)

    id_ruta             = Column(Integer, ForeignKey("ruta.id",          ondelete="RESTRICT"), nullable=False)
    id_usuario_sistema  = Column(Integer, ForeignKey("user_system.id",   ondelete="RESTRICT"), nullable=False)
    id_chofer           = Column(Integer, ForeignKey("choferes.id",      ondelete="RESTRICT"), nullable=False)
    id_camion           = Column(Integer, ForeignKey("camiones.id",      ondelete="RESTRICT"), nullable=False)

    fecha_creacion      = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    motivo_cancelacion = Column(String(255), nullable=True)

    ruta            = relationship("Ruta")
    usuario_sistema = relationship("UserSystem")
    chofer          = relationship("Chofer")
    camion          = relationship("Camion")

    servicios_cliente = relationship(
        "ServicioCliente",
        back_populates="servicio_transporte",
        cascade="all, delete-orphan"
    )

    ubicaciones = relationship(
        "UbicacionGPS",
        cascade="all, delete-orphan",
        order_by="UbicacionGPS.fecha_hora"
    )