from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    is_active: Optional[bool] = True
    address: Optional[str] = None
    create_at: Optional[str] = None
    update_at: Optional[str] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
