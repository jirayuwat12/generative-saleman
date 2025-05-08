from pydantic import BaseModel
from typing import Optional


class OrderBase(BaseModel):
    user_id: int
    session_id: int
    total_amount: float
    status: str  # "waiting", "pending", "completed", "cancelled"
    qr_reference: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
