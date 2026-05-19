from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.associations import menu_processes


class Process(Base):
    __tablename__ = "processes"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    code        = Column(String(50),  unique=True, nullable=False)
    description = Column(String(255))
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    menus = relationship("Menu", secondary=menu_processes, back_populates="processes")