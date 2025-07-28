# app/routes/auth.py
from typing         import List
from fastapi        import APIRouter, Depends, HTTPException, status
from sqlalchemy     import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models     import models
from app.schemas    import auth
from app.database   import get_db         # должен возвращать AsyncSession
from app.security   import get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])


# ——— Permissions CRUD ———

@router.post(
    "/permissions",
    response_model=auth.PermissionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    p: auth.PermissionCreate,
    db: AsyncSession = Depends(get_db),
):
    perm = models.Permission(code=p.code, description=p.description)
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm

@router.get(
    "/permissions",
    response_model=List[auth.PermissionRead],
)
async def list_permissions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Permission))
    return result.scalars().all()


# ——— Roles CRUD ———

@router.post(
    "/roles",
    response_model=auth.RoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    r: auth.RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    role = models.Role(name=r.name, description=r.description)
    if r.permission_ids:
        result = await db.execute(
            select(models.Permission).filter(models.Permission.id.in_(r.permission_ids))
        )
        role.permissions = result.scalars().all()
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role

@router.get(
    "/roles",
    response_model=List[auth.RoleRead],
)
async def list_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Role)
        .options(selectinload(models.Role.permissions))
    )
    return result.scalars().all()

@router.put(
    "/roles/{role_id}",
    response_model=auth.RoleRead,
)
async def update_role(
    role_id: int,
    r: auth.RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    # получаем роль
    role = await db.get(models.Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.name = r.name
    role.description = r.description
    if r.permission_ids:
        result = await db.execute(
            select(models.Permission).filter(models.Permission.id.in_(r.permission_ids))
        )
        role.permissions = result.scalars().all()

    await db.commit()
    await db.refresh(role)
    return role


# ——— Users CRUD ———

@router.post(
    "/users",
    response_model=auth.UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    u: auth.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    hash_ = get_password_hash(u.password)
    user = models.User(
        username=u.username,
        full_name=u.full_name,
        email=u.email,
        phone=u.phone,
        password_hash=hash_,
    )
    if u.role_ids:
        result = await db.execute(
            select(models.Role).filter(models.Role.id.in_(u.role_ids))
        )
        user.roles = result.scalars().all()

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.get(
    "/users",
    response_model=List[auth.UserRead],
)
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User)
        .options(
            # сначала грузим роли, а у ролей — их permissions
            selectinload(models.User.roles)
                .selectinload(models.Role.permissions)
        )
    )
    return result.scalars().all()

@router.get("/users/{user_id}", response_model=auth.UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User)
        .options(
            selectinload(models.User.roles)
                .selectinload(models.Role.permissions)
        )
        .filter(models.User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put(
    "/users/{user_id}",
    response_model=auth.UserRead,
)
async def update_user(
    user_id: int,
    u: auth.UserCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.full_name    = u.full_name
    user.email        = u.email
    user.phone        = u.phone
    if u.password:
        user.password_hash = get_password_hash(u.password)
    if u.role_ids:
        result = await db.execute(
            select(models.Role).filter(models.Role.id.in_(u.role_ids))
        )
        user.roles = result.scalars().all()

    await db.commit()
    await db.refresh(user)
    return user
