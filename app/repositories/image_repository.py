from sqlalchemy.orm import Session
from app.models.image import Image
from app.repositories.base import BaseRepository


class ImageRepository(BaseRepository[Image]):
    def __init__(self, db: Session):
        super().__init__(Image, db)

    def get_by_person_id(self, person_id: int) -> Image | None:
        return (
            self.db.query(Image)
            .filter(Image.person_id == person_id)
            .first()
        )