from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import BuildingConfig
from app.schemas.building_config import BuildingConfigCreate, BuildingConfigUpdate


async def get_configs(
        db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[BuildingConfig]:
    q = select(BuildingConfig).offset(skip).limit(limit)
    res = await db.execute(q)
    return res.scalars().all()


async def get_config(
        db: AsyncSession, config_id: UUID
) -> Optional[BuildingConfig]:
    q = select(BuildingConfig).where(BuildingConfig.id == config_id)
    res = await db.execute(q)
    return res.scalar_one_or_none()


async def create_config(
        db: AsyncSession, cfg: BuildingConfigCreate
) -> BuildingConfig:
    db_obj = BuildingConfig(**cfg.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_config(
        db: AsyncSession, config_id: UUID, patch: BuildingConfigUpdate
) -> Optional[BuildingConfig]:
    q = (
        update(BuildingConfig)
        .where(BuildingConfig.id == config_id)
        .values(**{k: v for k, v in patch.dict().items() if v is not None})
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(q)
    await db.commit()
    return await get_config(db, config_id)


async def delete_config(
        db: AsyncSession, config_id: UUID
) -> bool:
    q = delete(BuildingConfig).where(BuildingConfig.id == config_id)
    res = await db.execute(q)
    await db.commit()
    return res.rowcount > 0
