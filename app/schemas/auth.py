from typing import List, Optional
from pydantic import BaseModel, EmailStr


# ——— Permissions ———
class PermissionBase(BaseModel):
    code: str
    description: Optional[str]

class PermissionCreate(PermissionBase):
    pass

class PermissionRead(PermissionBase):
    id: int
    class Config:
        from_attributes = True


# ——— Roles ———
class RoleBase(BaseModel):
    name: str
    description: Optional[str]

class RoleCreate(RoleBase):
    permission_ids: List[int] = []
    class Config:
        from_attributes = True

class RoleRead(RoleBase):
    id: int
    permissions: List[PermissionRead] = []
    class Config:
        from_attributes = True


# ——— Users ———
class UserBase(BaseModel):
    username: str
    full_name: Optional[str]
    email: EmailStr
    tg_id: Optional[str]
    phone: Optional[str]

class UserCreate(UserBase):
    password: str
    role_ids: Optional[List[int]] = []

class UserRead(UserBase):
    id: int
    roles: List[RoleRead] = []
    class Config:
        from_attributes = True
