from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Image(Base):
    __tablename__ = "images"

    id         = Column(Integer, primary_key=True, index=True)
    person_id  = Column(
        Integer,
        ForeignKey("persons.id", ondelete="CASCADE"),
        unique=True,   # unique=True garantiza la cardinalidad 1:1
        nullable=False
    )
    name       = Column(String(255))          # nombre original del archivo
    image_url  = Column(String(500))          # URL pública de Cloudinary
    image_id   = Column(String(255))          # public_id de Cloudinary (para eliminar)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación inversa hacia Person
    person = relationship("Person", back_populates="image")