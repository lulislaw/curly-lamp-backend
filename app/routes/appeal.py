# backend/app/routes/appeal.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.appeal import AppealRead, AppealCreate, AppealUpdate, AppealHistoryRead
from app.crud.appeal import (
    get_appeals,
    get_appeal,
    create_appeal,
    update_appeal,
    soft_delete_appeal,
    get_appeal_history
)

router = APIRouter(
    prefix="/appeals",
    tags=["appeals"],
)

@router.get("/", response_model=list[AppealRead], summary="Список обращений")
async def read_appeals(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает список обращений с пагинацией.
    """
    return await get_appeals(db, skip=skip, limit=limit)


@router.get("/{appeal_id}", response_model=AppealRead, summary="Получить обращение по ID")
async def read_appeal(
        appeal_id: str,
        db: AsyncSession = Depends(get_db)
):
    appeal_obj = await get_appeal(db, appeal_id)
    if not appeal_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal not found")
    return appeal_obj


@router.post("/", response_model=AppealRead, status_code=status.HTTP_201_CREATED, summary="Создать новое обращение")
async def create_new_appeal(
    appeal_in: AppealCreate,
    db: AsyncSession = Depends(get_db),
    # здесь вы можете получать текущего пользователя через Depends, если у вас предусмотрена авторизация
    current_user_id: str = Depends(lambda: None)
):
    """
    Создаёт новое обращение.
    """
    new_appeal = await create_appeal(db, appeal_in, current_user_id)
    return new_appeal


@router.patch("/{appeal_id}", response_model=AppealRead, summary="Обновить обращение (частично)")
async def patch_appeal(
    appeal_id: str,
    appeal_in: AppealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(lambda: None)
):
    """
    Частично обновляет обращение (PATCH).
    """
    updated = await update_appeal(db, appeal_id, appeal_in, current_user_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal not found")
    return updated


@router.delete("/{appeal_id}", response_model=AppealRead, summary="Soft-delete обращения")
async def delete_appeal(
    appeal_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(lambda: None)
):
    """
    Soft-delete: помечает обращение как удалённое (is_deleted=True) и возвращает его.
    """
    deleted = await soft_delete_appeal(db, appeal_id, current_user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appeal not found")
    return deleted


@router.get("/{appeal_id}/history", response_model=list[AppealHistoryRead], summary="История изменений обращения")
async def read_appeal_history(
    appeal_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает историю изменений одного обращения.
    """
    history = await get_appeal_history(db, appeal_id)
    return history
