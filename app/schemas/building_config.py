# app/schemas/building_config.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class BuildingConfigBase(BaseModel):
    id_build: int
    name_build: str
    config: Dict[str, Any]

class BuildingConfigCreate(BuildingConfigBase):
    pass

class BuildingConfigUpdate(BaseModel):
    id_build: Optional[int]
    name_build: Optional[str]
    config: Optional[Dict[str, Any]]

class BuildingConfigRead(BuildingConfigBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
