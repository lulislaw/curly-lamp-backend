from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import app.crud.building_config as crud
import app.schemas.building_config as schemas

router = APIRouter(prefix="/building-configs", tags=["building-configs"])


@router.get("/", response_model=List[schemas.BuildingConfigRead])
async def list_building_configs(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
):
    return await crud.get_configs(db, skip, limit)


@router.get("/{config_id}", response_model=schemas.BuildingConfigRead)
async def get_building_config(
        config_id: UUID,
        db: AsyncSession = Depends(get_db),
):
    cfg = await crud.get_config(db, config_id)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Config not found")
    return cfg


@router.post("/", response_model=schemas.BuildingConfigRead, status_code=201)
async def create_building_config(
        in_cfg: schemas.BuildingConfigCreate,
        db: AsyncSession = Depends(get_db),
):
    return await crud.create_config(db, in_cfg)


@router.put("/{config_id}", response_model=schemas.BuildingConfigRead)
async def update_building_config(
        config_id: UUID,
        patch: schemas.BuildingConfigUpdate,
        db: AsyncSession = Depends(get_db),
):
    updated = await crud.update_config(db, config_id, patch)
    if updated is None:
        raise HTTPException(status_code=404, detail="Config not found")
    return updated


@router.delete("/{config_id}", response_model=bool)
async def delete_building_config(
        config_id: UUID,
        db: AsyncSession = Depends(get_db),
):
    ok = await crud.delete_config(db, config_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Config not found")
    return ok
