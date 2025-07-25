from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.models import AppealType, SeverityLevel, AppealStatus
from app.schemas.reference import AppealTypeRead, SeverityLevelRead, AppealStatusRead

router = APIRouter(
    prefix="/reference",
    tags=["reference"],
)


@router.get("/appeal_types/", response_model=list[AppealTypeRead], summary="Справочник: типы обращений")
async def read_appeal_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppealType).order_by(AppealType.sort_order))
    types = result.scalars().all()
    return types or []


@router.get("/severity_levels/", response_model=list[SeverityLevelRead], summary="Справочник: уровни серьёзности")
async def read_severity_levels(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SeverityLevel).order_by(SeverityLevel.priority))
    levels = result.scalars().all()
    return levels or []


@router.get("/appeal_statuses/", response_model=list[AppealStatusRead], summary="Справочник: статусы обращений")
async def read_appeal_statuses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AppealStatus).order_by(AppealStatus.sort_order))
    statuses = result.scalars().all()
    return statuses or []
