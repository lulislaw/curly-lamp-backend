# app/routes/building_config.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud.building_config import (create_config,get_configs,get_config,delete_config,update_config)
from app.schemas.building_config import (BuildingConfigRead,BuildingConfigCreate,BuildingConfigUpdate,BuildingConfigBase)
router = APIRouter(prefix="/building-configs", tags=["building-configs"])

@router.get("/", response_model=List[BuildingConfigRead])
async def read_configs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await get_configs(db, skip, limit)

@router.get("/{config_id}", response_model=BuildingConfigRead)
async def read_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    cfg = await get_config(db, config_id)
    if cfg is None:
        raise HTTPException(404, "Config not found")
    return cfg

@router.post(
    "/",
    response_model=BuildingConfigRead,
    status_code=201,
)
async def create_config(
    config_in: BuildingConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_config(db, config_in)

@router.put(
    "/{config_id}",
    response_model=BuildingConfigRead,
)
async def update_config(
    config_id: UUID,
    patch: BuildingConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated = await update_config(db, config_id, patch)
    if updated is None:
        raise HTTPException(404, "Config not found")
    return updated

@router.delete("/{config_id}", response_model=bool)
async def delete_config(
    config_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    ok = await delete_config(db, config_id)
    if not ok:
        raise HTTPException(404, "Config not found")
    return ok
