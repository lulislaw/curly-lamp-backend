from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import auth
from app.crud.auth import (
    list_permissions, create_permission, delete_permission, get_permission,
    list_roles, create_role, update_role, delete_role, get_role,
    list_users, create_user, update_user, delete_user, get_user
)
from sqlalchemy.exc import IntegrityError
router = APIRouter(prefix="/auth", tags=["auth"])


# ——— Permissions CRUD ———

@router.post(
    "/permissions",
    response_model=auth.PermissionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission_endpoint(
    p: auth.PermissionCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_permission(db, p)


@router.get(
    "/permissions",
    response_model=List[auth.PermissionRead],
)
async def list_permissions_endpoint(db: AsyncSession = Depends(get_db)):
    return await list_permissions(db)


@router.delete(
    "/permissions/{permission_id}",
    response_model=bool,
)
async def delete_permission_endpoint(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
):
    perm = await delete_permission(db, permission_id)
    if not perm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return True


# ——— Roles CRUD ———

@router.post(
    "/roles",
    response_model=auth.RoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_role_endpoint(
    r: auth.RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_role(db, r)


@router.get(
    "/roles",
    response_model=List[auth.RoleRead],
)
async def list_roles_endpoint(db: AsyncSession = Depends(get_db)):
    return await list_roles(db)


@router.put(
    "/roles/{role_id}",
    response_model=auth.RoleRead,
)
async def update_role_endpoint(
    role_id: int,
    r: auth.RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    role = await update_role(db, role_id, r)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.delete(
    "/roles/{role_id}",
    response_model=bool,
)
async def delete_role_endpoint(
    role_id: int,
    db: AsyncSession = Depends(get_db),
):
    role = await delete_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return True


# ——— Users CRUD ———

@router.post(
    "/users",
    response_model=auth.UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_endpoint(
    u: auth.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        # 1) Создаём
        user = await create_user(db, u)
        # 2) Подтягиваем полностью (с ролями и правами)
        return await get_user(db, user.id)
    except IntegrityError as exc:
        # Откатываем транзакцию, чтобы сессия была целой
        await db.rollback()
        # Разбиение по ключам уникальных полей
        msg = str(exc.orig).lower()
        if "users_username_key" in msg:
            raise HTTPException(status_code=400, detail="Пользователь с таким username уже существует")
        if "users_email_key" in msg:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
        # можно добавить проверку для других уникальных полей (например, tg_id)
        # иначе кидаем внутрь как неизменённую
        raise


@router.get(
    "/users",
    response_model=List[auth.UserRead],
)
async def list_users_endpoint(db: AsyncSession = Depends(get_db)):
    return await list_users(db)


@router.get(
    "/users/{user_id}",
    response_model=auth.UserRead,
)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put(
    "/users/{user_id}",
    response_model=auth.UserRead,
)
async def update_user_endpoint(
    user_id: int,
    u: auth.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await update_user(db, user_id, u)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete(
    "/users/{user_id}",
    response_model=bool,
)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return True
