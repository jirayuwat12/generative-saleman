from supabase import Client
from generative_saleman.services.db_services.orders_contain_products_db import (
    delete_order_item_by_order_and_product,
    get_order_items_by_order_id,
)
from generative_saleman.services.db_services.products_db import get_product_by_name
from generative_saleman.services.db_services.orders_db import (
    get_lastest_order_by_user_id,
    update_order,
)
from generative_saleman.utils.check_session_id import check_session_id
from generative_saleman.utils.format_product_by_order_id import format_product_by_order_id


from generative_saleman.services.db_services.products_db import update_product_amount
from generative_saleman.services.db_services.orders_contain_products_db import (
    get_order_item_by_order_and_product,
)


def remove_product_from_cart(supabase: Client, product_name: str, session_id: int | None) -> dict:
    res = check_session_id(supabase, session_id)
    if not isinstance(res, int):
        return res
    user_id = res

    order = get_lastest_order_by_user_id(supabase, user_id)
    if (order is None) or (order.status != "waiting"):
        return {"status": "fail", "detail": "ไม่พบตะกร้าสินค้าที่แก้ไขได้"}

    product = get_product_by_name(supabase, product_name)
    if product is None:
        return {"status": "fail", "detail": f"ไม่พบสินค้า {product_name}"}

    # ดึงจำนวนใน order item ก่อนลบ
    item = get_order_item_by_order_and_product(supabase, order.id, product.product_id)
    if item is None:
        return {"status": "fail", "detail": f"ไม่พบ {product_name} ในตะกร้า"}

    # ลบสินค้าจากตะกร้า
    deleted = delete_order_item_by_order_and_product(supabase, order.id, product.product_id)
    if not deleted:
        return {"status": "fail", "detail": f"ไม่สามารถลบ {product_name} ได้"}

    # คืนจำนวนสินค้าให้ stock
    update_product_amount(supabase, product.product_id, product.amount + item.quantity)

    # คำนวณยอดรวมใหม่
    items = get_order_items_by_order_id(supabase, order.id)
    new_total = sum(i.price_per_unit * i.quantity for i in items)
    update_order(supabase, order.id, {"total_amount": new_total})

    summary = format_product_by_order_id(supabase, order=order)
    return {
        "status": "success",
        "detail": f"นำ {product.name} ออกจากตะกร้าแล้ว",
        "cart_summary": summary,
    }
