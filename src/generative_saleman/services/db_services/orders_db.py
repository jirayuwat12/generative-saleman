from typing import Optional
from supabase import Client
from generative_saleman.model.orders import Order, OrderCreate


def get_order_by_id(supabase: Client, order_id: int) -> Optional[Order]:
    result = supabase.table("orders").select("*").eq("id", order_id).limit(1).execute()
    data = result.data
    if data:
        return Order(**data[0])
    return None


def get_lastest_order_by_user_id(supabase: Client, user_id: int) -> Optional[Order]:
    result = (
        supabase.table("orders").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
    )
    if result.data:
        return Order(**result.data[0])
    return None


def is_ref_already_used(supabase: Client, ref_nbr: str) -> bool:
    result = supabase.table("orders").select("id").eq("qr_reference", ref_nbr).execute()
    return len(result.data or []) > 0


def update_order_qr_reference(supabase: Client, order_id: int, ref_nbr: str) -> None:
    supabase.table("orders").update({"qr_reference": ref_nbr, "status": "completed"}).eq("id", order_id).execute()


def create_order(supabase: Client, order_create: OrderCreate) -> Order:
    result = supabase.table("orders").insert(order_create.model_dump(exclude_unset=True, exclude={"id"})).execute()
    data = result.data[0]
    return Order(**data)


def update_order(supabase: Client, order_id: int, order_update: dict) -> Order:
    result = supabase.table("orders").update(order_update).eq("id", order_id).execute()
    data = result.data[0]
    return Order(**data)
