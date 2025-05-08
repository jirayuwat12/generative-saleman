from supabase import Client
from generative_saleman.services.db_services.orders_db import get_lastest_order_by_user_id, update_order
from generative_saleman.utils.check_session_id import check_session_id
from generative_saleman.services.db_services.orders_contain_products_db import get_order_items_by_order_id
from generative_saleman.services.db_services.products_db import get_product_by_id, update_product_amount


def cancel_lastest_order(supabase: Client, session_id: int | None) -> dict:
    res = check_session_id(supabase, session_id)
    if not isinstance(res, int):
        return res
    user_id = res
    order = get_lastest_order_by_user_id(supabase, user_id)
    if order is None:
        return {"status": "fail", "detail": "ไม่พบคำสั่งซื้อในระบบ"}

    if order.status not in ["waiting", "pending"]:
        return {"status": "fail", "detail": f"คำสั่งซื้อสถานะ '{order.status}' ไม่สามารถยกเลิกได้"}

    # คืนจำนวนสินค้าแต่ละชิ้นกลับเข้า stock
    items = get_order_items_by_order_id(supabase, order.id)
    for item in items:
        product = get_product_by_id(supabase, item.product_id)
        if product:
            new_amount = product.amount + item.quantity
            update_product_amount(supabase, product.product_id, new_amount)

    # ยกเลิกคำสั่งซื้อ
    update_order(supabase, order.id, {"status": "cancelled"})

    return {
        "status": "success",
        "detail": f"ยกเลิกคำสั่งซื้อหมายเลข {order.id} เรียบร้อยแล้ว",
        "cancelled_total": order.total_amount,
    }
