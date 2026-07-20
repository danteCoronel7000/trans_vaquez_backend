from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.associations import user_roles


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(50),  unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

        # ✅ AGREGAR:
    person_id  = Column(
        Integer,
        ForeignKey("persons.id", ondelete="SET NULL"),
        unique=True,
        nullable=True
    )
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    person = relationship("Person", back_populates="user", uselist=False)
