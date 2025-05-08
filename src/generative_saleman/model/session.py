from pydantic import BaseModel
from typing import Optional


class SessionBase(BaseModel):
    user_id: int
    is_active: bool = True


class SessionCreate(SessionBase):
    pass


class Session(SessionBase):
    id: int
    created_at: Optional[str] = None
    expired_at: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
