from supabase import Client
from typing import Optional

from generative_saleman.model.products import Product, ProductCreate


def get_product_by_id(supabase: Client, product_id: int) -> Optional[Product]:
    result = supabase.table("products").select("*").eq("product_id", product_id).limit(1).execute()
    data = result.data
    if data:
        return Product(**data[0])
    return None


def get_product_by_name(supabase: Client, name: str) -> Optional[Product]:
    result = supabase.table("products").select("*").ilike("name", name).limit(1).execute()
    data = result.data
    if data:
        return Product(**data[0])
    return None


def get_all_products(supabase: Client, page: int, nrows: int) -> list[Product]:
    start = (page - 1) * nrows
    end = start + nrows - 1  # Supabase uses inclusive range
    result = supabase.table("products").select("*").range(start, end).execute()

    products = [Product(**data) for data in result.data]
    return products


def create_product(supabase: Client, product_create: ProductCreate) -> Product:
    result = supabase.table("products").insert(product_create.model_dump(exclude_unset=True)).execute()
    data = result.data[0]
    return Product(**data)


def update_product(supabase: Client, product_id: int, product_update: dict) -> Product:
    result = supabase.table("products").update(product_update).eq("product_id", product_id).execute()
    data = result.data[0]
    return Product(**data)


def update_product_amount(supabase: Client, product_id: int, new_amount: int) -> None:
    supabase.table("products").update({"amount": new_amount}).eq("product_id", product_id).execute()
