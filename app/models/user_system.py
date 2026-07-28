from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserSystem(Base):
    __tablename__ = "user_system"

    id                  = Column(Integer, primary_key=True, index=True)
    person_id           = Column(
        Integer,
        ForeignKey("persons.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    is_active           = Column(Boolean, default=True, nullable=False)
    fecha_ultimo_acceso = Column(DateTime(timezone=True), nullable=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())

    # Relación hacia Person
    person = relationship("Person", back_populates="user_system")