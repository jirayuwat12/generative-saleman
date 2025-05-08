from supabase import Client
from generative_saleman.services.db_services.orders_db import get_lastest_order_by_user_id, update_order
from generative_saleman.services.db_services.orders_contain_products_db import get_order_items_by_order_id
from generative_saleman.services.db_services.products_db import get_product_by_id, update_product_amount
from generative_saleman.utils.check_session_id import check_session_id
from generative_saleman.utils.format_product_by_order_id import format_product_by_order_id


def reactivate_lastest_order(supabase: Client, session_id: int | None) -> dict:
    res = check_session_id(supabase, session_id)
    if not isinstance(res, int):
        return res
    user_id = res
    order = get_lastest_order_by_user_id(supabase, user_id)
    if not order:
        return {"status": "fail", "detail": "ไม่พบคำสั่งซื้อในระบบ"}

    if order.status != "cancelled":
        return {"status": "fail", "detail": f"คำสั่งซื้อสถานะ '{order.status}' ไม่สามารถนำกลับมาใช้ได้"}

    # ดึงรายการสินค้า
    items = get_order_items_by_order_id(supabase, order.id)
    if not items:
        return {"status": "fail", "detail": "คำสั่งซื้อเดิมไม่มีสินค้า ไม่สามารถเปิดกลับมาได้"}

    # ตรวจสอบ stock และคำนวณราคารวม
    total = 0.0
    insufficient = []
    for item in items:
        product = get_product_by_id(supabase, item.product_id)
        if not product:
            insufficient.append(f"[{item.product_id}] ไม่พบสินค้า")
            continue
        if product.amount < item.quantity:
            insufficient.append(f"{product.name} เหลือ {product.amount} ชิ้น (ต้องการ {item.quantity})")
        else:
            total += item.quantity * product.price

    if insufficient:
        return {
            "status": "fail",
            "detail": "ไม่สามารถเปิดคำสั่งซื้อ เนื่องจากสินค้าบางรายการมีจำนวนไม่พอ",
            "problem": insufficient,
        }

    # หัก stock
    for item in items:
        product = get_product_by_id(supabase, item.product_id)
        if product:
            new_amount = product.amount - item.quantity
            update_product_amount(supabase, product.product_id, new_amount)

    # เปิดสถานะใหม่
    update_order(supabase, order.id, {"status": "waiting", "total_amount": total})

    # สร้างสรุปตะกร้า
    summary = format_product_by_order_id(supabase, order=order)

    return {
        "status": "success",
        "detail": "นำคำสั่งซื้อที่ถูกยกเลิกกลับมาใช้งานอีกครั้ง และหักจำนวนสินค้าตามที่สั่งไว้",
        "cart_summary": summary,
    }
