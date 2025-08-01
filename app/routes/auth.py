from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.database import get_db
from app.schemas import auth
from app.crud.auth import (
    list_permissions, create_permission, delete_permission, get_permission,
    list_roles, create_role, update_role, delete_role, get_role,
    list_users, create_user, update_user, delete_user, get_user, get_user_by_username
)
from app.core.security import verify_password, create_access_token
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.auth import UserRead, UserCreate, Token
from app.models.models import User
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


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
    response_model=auth.RoleCreate,
    status_code=status.HTTP_201_CREATED,
)
async def create_role_endpoint(
        r: auth.RoleCreate,
        db: AsyncSession = Depends(get_db),
):
    try:
        role = await create_role(db, r)
        return role
    except IntegrityError as exc:
        await db.rollback()
        msg = str(exc.orig).lower()
        if "roles_name_key" in msg:
            detail = "Роль с таким именем уже существует"
        else:
            detail = "Нарушено уникальное ограничение"
        raise HTTPException(400, detail=detail)


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
    response_model=auth.UserBase,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_endpoint(
        u: auth.UserCreate,
        db: AsyncSession = Depends(get_db),
):
    try:
        user = await create_user(db, u)
        return await get_user(db, user.id)

    except IntegrityError as exc:
        await db.rollback()
        msg = str(exc.orig).lower()
        if "users_username_key" in msg:
            detail = "Пользователь с таким username уже существует"
        elif "users_email_key" in msg:
            detail = "Пользователь с таким email уже существует"
        elif "users_tg_id_key" in msg or "tg_id" in msg:
            detail = "Пользователь с таким Telegram ID уже существует"
        else:
            detail = "Нарушено уникальное ограничение"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


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
    try:
        await update_user(db, user_id, u)
        return await get_user(db, user_id)

    except IntegrityError as exc:
        await db.rollback()
        msg = str(exc.orig).lower()
        if "users_username_key" in msg:
            detail = "Пользователь с таким username уже существует"
        elif "users_email_key" in msg:
            detail = "Пользователь с таким email уже существует"
        elif "users_tg_id_key" in msg or "tg_id" in msg:
            detail = "Пользователь с таким Telegram ID уже существует"
        else:
            detail = "Нарушено уникальное ограничение"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


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

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учётные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(db, username)
    if not user:
        raise credentials_exception
    return user


@router.get(
    "/users_me",
    response_model=auth.UserRead,
    summary="Профиль текущего пользователя"
)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # вместо «сырых» связей — дёрнем полностью через get_user
    user_full = await get_user(db, current_user.id)
    if not user_full:
        # на всякий случай
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_full


@router.post("/users_reg", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(u: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, u)
    return await get_user(db, user.id)

def require_permissions(*permission_codes: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        # подгружаем роли+права
        user = await get_user(db, current_user.id)  # selectinload(User.roles)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        # собираем все коды прав
        user_perms = {perm.code for role in user.roles for perm in role.permissions}
        missing = set(permission_codes) - user_perms
        if missing:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав: {', '.join(missing)}"
            )
        return user
    return dependency

@router.get(
    "/secure-data",
    response_model=dict,
    summary="Только для тех у кого есть право 'view_secure_data'"
)
async def secure_data(
    user: User = Depends(require_permissions("view_secure_data"))
):
    return {"msg": f"Привет, {user.username}! У тебя есть доступ к secure-data."}
