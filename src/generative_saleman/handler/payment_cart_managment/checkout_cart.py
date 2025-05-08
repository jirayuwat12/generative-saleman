from supabase import Client

from generative_saleman.services.db_services.orders_contain_products_db import get_order_items_by_order_id
from generative_saleman.services.db_services.orders_db import get_lastest_order_by_user_id, update_order
from generative_saleman.services.qr_services import generate_qr_code
from generative_saleman.utils.check_session_id import check_session_id
from generative_saleman.utils.format_product_by_order_id import format_product_by_order_id


def checkout_cart(supabase: Client, session_id: int | None) -> dict:
    res = check_session_id(supabase, session_id)
    if not isinstance(res, int):
        return res
    user_id = res
    # 2. ดึง order ล่าสุด
    order = get_lastest_order_by_user_id(supabase, user_id)
    if (order is None) or (order.status != "waiting"):
        return {"status": "fail", "detail": "ไม่มีตะกร้าที่พร้อมจะชำระ กรุณาเพิ่มสินค้าก่อน"}

    # 3. ตรวจสอบว่าสินค้าในตะกร้ามีจริงไหม
    items = get_order_items_by_order_id(supabase, order.id)
    if len(items) == 0:
        return {"status": "fail", "detail": "ในตะกร้ายังไม่มีสินค้า กรุณาเพิ่มสินค้าก่อน"}

    # 4. เปลี่ยนสถานะ order เป็น "pending"
    update_order(supabase, order.id, {"status": "pending"})

    # 5. สรุปรายการสินค้า
    summary = format_product_by_order_id(supabase=supabase, order=order)

    # 6. สร้าง QR สำหรับจ่ายเงิน
    phone_nbr = "0613261566"
    qr_base64 = generate_qr_code(phone_nbr=phone_nbr, amount=order.total_amount)

    # 7. ส่งกลับ
    return {
        "status": "success",
        "detail": "สร้างรายการคำสั่งซื้อเรียบร้อย กรุณาชำระเงินตามรายการด้านล่าง",
        "cart_summary": summary,
        "qr_base64": qr_base64,
        "payment_info": f"ชำระเงินจำนวน {order.total_amount:.2f} บาท ผ่าน QR ด้านล่าง เบอร์ PromptPay {phone_nbr}",
    }
