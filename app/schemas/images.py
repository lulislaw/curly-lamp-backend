from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ImageRead(BaseModel):
    id: UUID
    filename: str
    filepath: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
