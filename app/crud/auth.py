from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.core.security import get_password_hash
from app.models.models import Permission, Role, User
from app.schemas.auth import (
    PermissionCreate, RoleCreate, UserCreate, )

from fastapi import HTTPException, status
# ——— Permissions ———

async def get_permission(db: AsyncSession, permission_id: int) -> Optional[Permission]:
    return await db.get(Permission, permission_id)


async def list_permissions(db: AsyncSession) -> List[Permission]:
    result = await db.execute(select(Permission))
    return result.scalars().all()


async def create_permission(
    db: AsyncSession,
    p: PermissionCreate
) -> Permission:
    perm = Permission(code=p.code, description=p.description)
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm


async def delete_permission(
    db: AsyncSession,
    permission_id: int
) -> Permission:
    perm = await get_permission(db, permission_id)
    if not perm:
        return None
    await db.delete(perm)
    await db.commit()
    return perm


# ——— Roles ———

async def get_role(db: AsyncSession, role_id: int) -> Optional[Role]:
    return await db.get(Role, role_id)


async def list_roles(db: AsyncSession) -> List[Role]:
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions))
    )
    return result.scalars().all()


async def create_role(
    db: AsyncSession,
    r: RoleCreate
) -> Role:
    role = Role(name=r.name, description=r.description)
    if r.permission_ids:
        perms = (await db.execute(
            select(Permission).filter(Permission.id.in_(r.permission_ids))
        )).scalars().all()
        role.permissions = perms
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(
    db: AsyncSession,
    role_id: int,
    r: RoleCreate
) -> Optional[Role]:
    # Загрузим роль вместе с текущими permission-ами
    result = await db.execute(
        select(Role)
        .options(selectinload(Role.permissions))
        .filter(Role.id == role_id)
    )
    role = result.scalars().first()

    if not role:
        return None

    # Теперь можно менять поля и список permissions
    role.name = r.name
    role.description = r.description

    if r.permission_ids:
        perms = (
            await db.execute(
                select(Permission).filter(Permission.id.in_(r.permission_ids))
            )
        ).scalars().all()
        role.permissions = perms

    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(
    db: AsyncSession,
    role_id: int
) -> Role:
    role = await get_role(db, role_id)
    if not role:
        return None
    await db.delete(role)
    await db.commit()
    return role


# ——— Users ———

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles)
                .selectinload(Role.permissions)
        )
        .filter(User.id == user_id)
    )
    return result.scalars().first()


async def list_users(db: AsyncSession) -> List[User]:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles)
                .selectinload(Role.permissions)
        )
    )
    return result.scalars().all()


async def create_user(
    db: AsyncSession,
    u: UserCreate
) -> User:
    hash_ = get_password_hash(u.password)
    user = User(
        username=u.username,
        full_name=u.full_name,
        email=u.email,
        phone=u.phone,
        password_hash=hash_,
    )
    if u.role_ids:
        roles_ = (await db.execute(
            select(Role).filter(Role.id.in_(u.role_ids))
        )).scalars().all()
        user.roles = roles_
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession,
    user_id: int,
    u: UserCreate
) -> None:
    # грузим сразу с ролями
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .filter(User.id==user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    user.username = u.username
    user.full_name = u.full_name
    user.email     = u.email
    user.phone     = u.phone
    if u.password:
        user.password_hash = get_password_hash(u.password)

    if u.role_ids is not None:
        roles_res = await db.execute(
            select(Role).filter(Role.id.in_(u.role_ids))
        )
        user.roles = roles_res.scalars().all()

    await db.commit()
    await db.refresh(user)


async def delete_user(
    db: AsyncSession,
    user_id: int
) -> User:
    user = await get_user(db, user_id)
    if not user:
        return None
    await db.delete(user)
    await db.commit()
    return user

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()