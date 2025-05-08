from supabase import Client
from generative_saleman.model.orders import Order
from generative_saleman.services.db_services.orders_contain_products_db import get_order_items_by_order_id
from generative_saleman.services.db_services.products_db import get_product_by_id


def format_product_by_order_id(supabase: Client, order: Order):
    items = get_order_items_by_order_id(supabase, order.id)
    lines = []
    for i, item in enumerate(items, 1):
        product = get_product_by_id(supabase, item.product_id)
        if product is None:
            raise ValueError(f"ไม่พบสินค้า {item.product_id}")
        line = f"{i}. {product.name} x {item.quantity} ชิ้น = {item.price_per_unit * item.quantity:.2f} บาท"
        lines.append(line)
    summary = "\n".join(lines) + f"\n\nรวมทั้งหมด: {order.total_amount:.2f} บาท"
    return summary
