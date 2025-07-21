# app/crud/image.py
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Image

async def create_image(db: AsyncSession, filename: str, filepath: str) -> Image:
    img = Image(filename=filename, filepath=filepath)
    db.add(img)
    await db.commit()
    await db.refresh(img)
    return img

async def list_images(db: AsyncSession) -> list[Image]:
    q = select(Image).order_by(Image.uploaded_at.desc())
    res = await db.execute(q)
    return res.scalars().all()
