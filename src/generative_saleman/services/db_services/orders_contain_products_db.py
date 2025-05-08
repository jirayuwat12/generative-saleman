from supabase import Client
from generative_saleman.model.orders_contain_products import OrderItem, OrderItemCreate


def get_order_items_by_order_id(supabase: Client, order_id: int) -> list[OrderItem]:
    result = supabase.table("orders_contain_products").select("*").eq("order_id", order_id).execute()
    items = result.data or []
    return [OrderItem(**item) for item in items]


def get_order_item_by_order_and_product(supabase: Client, order_id: int, product_id: int):
    response = (
        supabase.table("orders_contain_products")
        .select("*")
        .eq("order_id", order_id)
        .eq("product_id", product_id)
        .limit(1)
        .execute()
    )
    return response.data[0] if response.data else None


def delete_order_item_by_order_and_product(supabase: Client, order_id: int, product_id: int) -> bool:
    result = (
        supabase.table("orders_contain_products")
        .delete()
        .eq("order_id", order_id)
        .eq("product_id", product_id)
        .execute()
    )
    return result.data is not None and len(result.data) > 0


def create_order_item(supabase: Client, item_create: OrderItemCreate) -> OrderItem:
    result = supabase.table("orders_contain_products").insert(item_create.model_dump(exclude_unset=True)).execute()
    data = result.data[0]
    return OrderItem(**data)


def bulk_create_order_items(supabase: Client, items_create: list[OrderItemCreate]) -> list[OrderItem]:
    payload = [item.model_dump(exclude_unset=True) for item in items_create]
    result = supabase.table("orders_contain_products").insert(payload).execute()
    items = result.data or []
    return [OrderItem(**item) for item in items]
