from datetime import datetime

from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    price: float
    amount: int


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    def format_product(self) -> str:
        return "{} ราคา {} บาท เหลืออยู่ {} ชิ้น".format(self.name, self.price, self.amount)
