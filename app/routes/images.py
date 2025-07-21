# app/routes/images.py
import os

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.database import get_db
from app.crud.images import create_image, list_images
from app.schemas.images import ImageRead

router = APIRouter(prefix="/images", tags=["images"])

# куда сохраняем файлы
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=ImageRead, status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".gif"):
        raise HTTPException(400, "Поддерживаются только изображения JPG/PNG/GIF")
    # генерим уникальное имя
    new_name = f"{uuid4().hex}{ext}"
    dst = os.path.join(UPLOAD_DIR, new_name)
    # сохраняем на диск
    try:
        contents = await file.read()
        async with aiofiles.open(dst, "wb") as f:
            await f.write(contents)
    except Exception as e:
        raise HTTPException(500, f"Не удалось сохранить файл: {e}")

    # сохраняем метаданные в БД
    img = await create_image(db, filename=new_name, filepath=dst)
    return img

@router.get("/", response_model=list[ImageRead])
async def get_images(db: AsyncSession = Depends(get_db)):
    return await list_images(db)
