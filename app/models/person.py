from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class GenderEnum(str, enum.Enum):
    MASCULINO = "MASCULINO"
    FEMENINO  = "FEMENINO"


class Person(Base):
    __tablename__ = "persons"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"),
                         unique=True, nullable=True)  # unique = cardinalidad 1:1 cuando existe usuario

    # Nombre
    first_name  = Column(String(100), nullable=False)
    last_name   = Column(String(100), nullable=False)

    # Documento
    ci          = Column(String(20), unique=True, nullable=False)

    # Género
    gender      = Column(Enum(GenderEnum), nullable=False)

    # Fecha de nacimiento — edad se calcula, no se guarda
    birth_date  = Column(Date, nullable=False)

    # Contacto
    phone       = Column(String(20))
    address     = Column(String(255))
    city        = Column(String(100))
    country     = Column(String(100), default="Bolivia")

    # Foto de perfil
    photo_url   = Column(String(500))

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación inversa hacia User
    user = relationship("User", back_populates="person")
