from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.camera_hardware import (
    create_camera,
    get_camera,
    get_cameras,
    delete_camera
)
from app.schemas.camera_hardware import (
    CameraHardwareRead,
    CameraHardwareCreate,
)
from app.database import get_db

router = APIRouter(tags=["cameras"], prefix="/cameras")


@router.get("/", response_model=List[CameraHardwareRead])
async def read_cameras(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
):
    return await get_cameras(db, skip, limit)


@router.get("/{camera_id}", response_model=CameraHardwareRead)
async def read_camera(
        camera_id: str,
        db: AsyncSession = Depends(get_db),
):
    cam = await get_camera(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam


@router.post("/", response_model=CameraHardwareRead, status_code=201)
async def create_camera_endpoint(
        camera: CameraHardwareCreate,
        db: AsyncSession = Depends(get_db),
):
    return await create_camera(db, camera)


@router.delete("/{camera_id}", response_model=bool)
async def delete_camera_endpoint(
        camera_id: str,
        db: AsyncSession = Depends(get_db),
):
    ok = await delete_camera(db, camera_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Camera not found")
    return ok
