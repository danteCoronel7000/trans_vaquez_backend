from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.associations import role_menus, menu_processes


class Menu(Base):
    __tablename__ = "menus"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    path       = Column(String(255))
    icon       = Column(String(50))
    order      = Column(Integer, default=0)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    roles     = relationship("Role",    secondary=role_menus,     back_populates="menus")
    processes = relationship("Process", secondary=menu_processes,  back_populates="menus")