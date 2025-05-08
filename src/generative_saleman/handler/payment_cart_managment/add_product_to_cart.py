from supabase import Client
from generative_saleman.model.orders import OrderCreate
from generative_saleman.model.orders_contain_products import OrderItemCreate
from generative_saleman.services.db_services.orders_contain_products_db import (
    create_order_item,
)
from generative_saleman.services.db_services.orders_db import create_order, get_lastest_order_by_user_id, update_order
from generative_saleman.services.db_services.products_db import get_product_by_name, update_product_amount
from generative_saleman.utils.check_session_id import check_session_id
from generative_saleman.utils.format_product_by_order_id import format_product_by_order_id


def add_product_to_cart(supabase: Client, product_name: str, quantity: int, session_id: int | None) -> dict:
    res = check_session_id(supabase, session_id)
    if not isinstance(res, int):
        return res
    user_id = res

    # 1. คำสั่งซื้อล่าสุด
    order = get_lastest_order_by_user_id(supabase, user_id)
    if (order is None) or (order.status == "completed") or (order.status == "cancelled"):
        new_order = OrderCreate(user_id=user_id, session_id=session_id, total_amount=0.0, status="waiting")  # type: ignore
        order = create_order(supabase, new_order)
    elif order.status == "pending":
        summary = format_product_by_order_id(supabase=supabase, order=order)
        return {
            "status": "warn",
            "detail": "คุณมีคำสั่งซื้อที่ยังไม่ชำระเงิน กรุณายกเลิกหรือจ่ายเงินให้เรียบร้อยก่อนเพิ่มหรือลดสินค้า",
            "cart_summary": summary,
        }

    # 2. ตรวจสอบสินค้า
    product = get_product_by_name(supabase, product_name)
    if product is None:
        return {"status": "fail", "detail": f"ไม่พบสินค้า {product_name}"}
    if product.amount < quantity:
        return {"status": "fail", "detail": f"จำนวนสินค้าคงเหลือไม่พอ ({product.amount} ชิ้น)"}

    # 3. เพิ่มใน order_items
    item = OrderItemCreate(
        order_id=order.id,
        product_id=product.product_id,
        quantity=quantity,
        price_per_unit=product.price,
    )
    create_order_item(supabase, item)

    # 4. อัปเดตยอดรวม
    total_price = product.price * quantity
    new_total_amount = order.total_amount + total_price
    update_order(supabase, order.id, {"total_amount": new_total_amount})

    # 5. หักจำนวนสินค้าออกจาก stock
    new_amount = product.amount - quantity
    update_product_amount(supabase, product.product_id, new_amount)

    # 6. สรุปตะกร้า
    summary = format_product_by_order_id(supabase=supabase, order=order)
    return {
        "status": "success",
        "detail": f"เพิ่ม {product.name} x{quantity} เข้าออเดอร์ใหม่แล้ว ราคารวม {total_price:.2f} บาท",
        "cart_summary": summary,
    }
