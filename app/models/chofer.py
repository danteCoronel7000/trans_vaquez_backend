from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.database import Base
import enum


class CategoriaEnum(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class Chofer(Base):
    __tablename__ = "choferes"

    id        = Column(Integer, primary_key=True, index=True)
    person_id = Column(
        Integer,
        ForeignKey("persons.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    licencia   = Column(String(50), unique=True, nullable=False)
    categoria  = Column(SAEnum(CategoriaEnum), nullable=False)
    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación hacia Person
    person = relationship("Person", back_populates="chofer")