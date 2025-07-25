from __future__ import annotations
import datetime
import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class AppealBase(BaseModel):
    type_id: int
    severity_id: int
    status_id: int
    location: Optional[str] = None
    description: Optional[str] = None
    reporter_id: Optional[uuid.UUID] = None
    source: str
    assigned_to_id: Optional[uuid.UUID] = None
    payload: Optional[dict] = None


class AppealCreate(AppealBase):
    pass


class AppealUpdate(BaseModel):
    status_id: Optional[int] = None
    assigned_to_id: Optional[uuid.UUID] = None
    location: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None
    is_deleted: Optional[bool] = None


class AppealRead(AppealBase):
    id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
    ticket_number: int
    is_deleted: bool
    type_name: str
    severity_name: str
    status_name: str

    class Config:
        from_attributes = True


class AppealHistoryBase(BaseModel):
    event_time: datetime.datetime
    event_type: str
    changed_by_id: Optional[uuid.UUID] = None
    payload: Optional[dict] = None


class AppealHistoryRead(AppealHistoryBase):
    id: uuid.UUID
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class AppealTypeRead(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True  # для SQLAlchemy ORM


class SeverityLevelRead(BaseModel):
    id: int
    code: str
    name: str
    priority: int

    class Config:
        from_attributes = True


class AppealStatusRead(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True
