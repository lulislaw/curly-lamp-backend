# app/crud/camera_hardware.py

import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import CameraHardware
from app.schemas.camera_hardware import CameraHardwareCreate

async def get_cameras(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(CameraHardware).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_camera(db: AsyncSession, camera_id: uuid.UUID):
    stmt = select(CameraHardware).where(CameraHardware.id == camera_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def create_camera(db: AsyncSession, cam_in: CameraHardwareCreate):
    data = cam_in.dict()
    db_cam = CameraHardware(**data)
    db.add(db_cam)
    await db.commit()
    await db.refresh(db_cam)
    return db_cam

async def delete_camera(db: AsyncSession, camera_id: uuid.UUID) -> bool:
    stmt = (
        delete(CameraHardware)
        .where(CameraHardware.id == camera_id)
        .execution_options(synchronize_session="fetch")
    )
    result = await db.execute(stmt)
    await db.commit()
    # rowcount вернёт число удалённых строк
    return result.rowcount > 0
