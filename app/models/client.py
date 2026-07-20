from sqlalchemy import Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.core.database import Base


class Client(Base):
    __tablename__ = "clients"

    id        = Column(Integer, primary_key=True, index=True)
    person_id = Column(
        Integer,
        ForeignKey("persons.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    nit           = Column(String(20), unique=True, nullable=True)
    razon_social  = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación hacia Person
    person = relationship("Person", back_populates="client")