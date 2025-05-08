from supabase import Client
from generative_saleman.model.orders import OrderCreate
from generative_saleman.services.db_services.orders_db import create_order, get_lastest_order_by_user_id
from generative_saleman.utils.check_session_id import check_session_id
from generative_saleman.utils.format_product_by_order_id import format_product_by_order_id


def cart_summary(supabase: Client, session_id: int | None) -> dict:
    res = check_session_id(supabase, session_id)
    if not isinstance(res, int):
        return res
    user_id = res

    order = get_lastest_order_by_user_id(supabase, user_id)
    if not order:
        order = create_order(
            supabase, OrderCreate(user_id=user_id, session_id=session_id, total_amount=0.0, status="waiting")  # type: ignore
        )

    if order.status not in ["waiting", "pending"]:
        return {"status": "fail", "detail": f"ไม่สามารถสรุปรายการได้ เนื่องจากสถานะคำสั่งซื้อคือ '{order.status}'"}

    summary = format_product_by_order_id(supabase, order=order)

    return {"status": "success", "detail": "รายการคำสั่งซื้อของคุณ", "cart_summary": summary}
