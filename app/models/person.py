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
    # Nombre
    first_name  = Column(String(100), nullable=False)
    last_name   = Column(String(100), nullable=False)
    #gmail
    gmail = Column(String(150), unique=True, nullable=True)

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

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación inversa hacia User
    # models/person.py
    user = relationship("User", back_populates="person", uselist=False)

        # ── Nueva relación 1:1 hacia Image ───────────────
    image = relationship(
        "Image",
        back_populates="person",
        uselist=False,              # uselist=False = cardinalidad 1:1
        cascade="all, delete-orphan"
    )
    # Agregar dentro de la clase Person
    client = relationship("Client", back_populates="person", uselist=False)
