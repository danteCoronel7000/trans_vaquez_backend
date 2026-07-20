from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ImageOut(BaseModel):
    id:        int
    person_id: int
    name:      Optional[str]
    image_url: Optional[str]
    image_id:  Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}