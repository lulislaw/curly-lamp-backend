from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class CameraHardwareBase(BaseModel):
    name: str
    stream_url: str
    ptz_enabled: Optional[bool] = False
    ptz_protocol: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class CameraHardwareCreate(CameraHardwareBase):
    pass


class CameraHardwareRead(CameraHardwareBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
