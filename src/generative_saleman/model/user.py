from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    name: str
    phone: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    email: str | None
    is_active: Optional[bool] = True
    address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
