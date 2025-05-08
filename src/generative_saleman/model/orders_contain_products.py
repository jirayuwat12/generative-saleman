from pydantic import BaseModel


class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price_per_unit: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
