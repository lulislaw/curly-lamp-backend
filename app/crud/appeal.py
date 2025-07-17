# backend/app/crud/appeal.py

from typing import List, Optional
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Appeal, AppealHistory
from app.schemas.appeal import AppealCreate, AppealUpdate
from sqlalchemy.orm import joinedload
from app.ws_manager import manager
async def get_appeal(db: AsyncSession, appeal_id: uuid.UUID) -> Optional[Appeal]:
    stmt = (
        select(Appeal)
        .options(
            joinedload(Appeal.type),
            joinedload(Appeal.severity),
            joinedload(Appeal.status),
        )
        .where(Appeal.id == appeal_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_appeals(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Appeal]:
    result = await db.execute(
        select(Appeal).where(Appeal.is_deleted == False).order_by(Appeal.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()



async def create_appeal(db: AsyncSession, appeal_in: AppealCreate, current_user_id: str) -> Appeal:
    new_obj = Appeal(
        type_id=appeal_in.type_id,
        severity_id=appeal_in.severity_id,
        status_id=appeal_in.status_id,
        location=appeal_in.location,
        description=appeal_in.description,
        reporter_id=appeal_in.reporter_id,
        source=appeal_in.source,
        assigned_to_id=appeal_in.assigned_to_id,
        payload=appeal_in.payload or {},
    )
    db.add(new_obj)
    await db.commit()
    await db.refresh(new_obj)

    # Формируем сообщение для рассылки
    message = {
        "event_type": "create",
        "id": str(new_obj.id),

    }
    print(message, "aaaaaaaaaa")
    # Рассылаем всем подписанным WebSocket-клиентам
    await manager.broadcast(message)

    return new_obj


async def update_appeal(db: AsyncSession, appeal_id: str, appeal_in: AppealUpdate, current_user_id: str) -> Appeal | None:
    stmt = select(Appeal).where(Appeal.id == appeal_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        return None

    # Проверяем, какие поля пришли, и меняем
    if appeal_in.status_id is not None:
        obj.status_id = appeal_in.status_id
    if appeal_in.assigned_to_id is not None:
        obj.assigned_to_id = appeal_in.assigned_to_id
    if appeal_in.location is not None:
        obj.location = appeal_in.location
    if appeal_in.description is not None:
        obj.description = appeal_in.description

    await db.commit()
    await db.refresh(obj)

    # Снова формируем сообщение для рассылки
    message = {
        "event_type": "update",
        "appeal": {
            "id": str(obj.id),
            "type_id": obj.type_id,
            "type_name": obj.type_name,
            "severity_id": obj.severity_id,
            "severity_name": obj.severity_name,
            "status_id": obj.status_id,
            "status_name": obj.status_name,
            "location": obj.location,
            "description": obj.description,
            "source": obj.source,
            "reporter_id": str(obj.reporter_id) if obj.reporter_id else None,
            "assigned_to_id": str(obj.assigned_to_id) if obj.assigned_to_id else None,
            "payload": obj.payload,
            "is_deleted": obj.is_deleted,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
        },
    }
    await manager.broadcast(message)

    return obj


async def soft_delete_appeal(db: AsyncSession, appeal_id: str, current_user_id: str) -> Appeal | None:
    stmt = select(Appeal).where(Appeal.id == appeal_id)
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        return None

    # Вместо физического удаления ставим флаг is_deleted = True
    obj.is_deleted = True
    await db.commit()
    await db.refresh(obj)

    # Сообщаем всем, что объект «удален»
    message = {
        "event_type": "delete",
        "appeal": {
            "id": str(obj.id),
            # Можно передать минимум полей — достаточно id и флага is_deleted.
            "is_deleted": obj.is_deleted,
        },
    }
    await manager.broadcast(message)

    return obj


async def get_appeal_history(db: AsyncSession, appeal_id: uuid.UUID) -> List[AppealHistory]:
    result = await db.execute(
        select(AppealHistory).where(AppealHistory.appeal_id == appeal_id).order_by(AppealHistory.event_time.desc())
    )
    return result.scalars().all()
