from functools import wraps
from generative_saleman.handler.payment_cart_managment import (
    add_product_to_cart,
    checkout_cart,
    decode_slip_and_verify,
    cancel_lastest_order,
    remove_product_from_cart,
    reactivate_lastest_order,
    cart_summary,
)
from generative_saleman.services.db_services.base import get_supabase_client
from mcp.server.fastmcp import FastMCP

from generative_saleman.utils.get_log import get_log

log = get_log("_payment_cart_managment.py")


def log_function_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log.info(f"📌 Called function: {func.__name__}")
        if args:
            log.info(f"  - Positional args: {args}")
        if kwargs:
            log.info(f"  - Keyword args: {kwargs}")
        result = func(*args, **kwargs)
        log.info(f"  - Result: {result}")
        return result

    return wrapper


def register(mcp: FastMCP) -> FastMCP:
    # Add product to cart
    supabase = get_supabase_client()

    @mcp.tool(name="add_product_to_cart", description="เพิ่มสินค้าลงในตะกร้าสินค้า")
    @log_function_call
    def mcp_add_product_to_cart(product_name: str, quantity: int, session_id: int | None = None) -> dict:
        """
        เพิ่มสินค้าเข้าไปในตะกร้าของผู้ใช้ตาม session ที่กำหนด

        ฟังก์ชันนี้จะ:
        - ตรวจสอบ session และดึง user_id
        - ดึง order ล่าสุดของผู้ใช้ ถ้าไม่มีหรือถูกปิดแล้ว จะสร้าง order ใหม่ (status="waiting")
        - ถ้า order ล่าสุดเป็น "pending" จะเตือนให้ชำระเงินก่อน
        - ตรวจสอบว่ามีสินค้านั้นอยู่ในระบบหรือไม่
        - เพิ่มสินค้าและจำนวนลงใน order_items
        - อัปเดตยอดรวม (total_amount) ของ order
        - คืนข้อความสรุปตะกร้าสินค้า

        ใช้กรณีที่ลูกค้าถาม:
        - "ขอเพิ่ม Dixit สองกล่อง"
        - "อยากได้ Codenames อีก 1 อัน"
        - "ใส่ Pandemic ลงตะกร้าให้หน่อย"
        - "สั่งซื้อ Root 3 กล่องเลยครับ"

        Args:
            product_name (str): ชื่อของสินค้าที่ต้องการเพิ่ม
            quantity (int): จำนวนสินค้าที่ต้องการเพิ่ม
            session_id (int | None): รหัส session ของผู้ใช้

        Returns:
            dict:
                - status (str): สถานะของผลลัพธ์ ("success", "fail", "warn")
                - detail (str): ข้อความอธิบายเพิ่มเติม
                - cart_summary (str, optional): สรุปรายการสินค้าในตะกร้า (เมื่อสำเร็จหรือมีการเตือน)
        """
        return add_product_to_cart(supabase, product_name, quantity, session_id)

    # Checkout Cart
    @mcp.tool(name="checkout_cart", description="ชำระเงินตะกร้าสินค้า และสร้าง QR")
    @log_function_call
    def mcp_checkout_cart(session_id: int | None = None) -> dict:
        """
        ทำการ checkout ตะกร้าสินค้าของผู้ใช้ และสร้าง QR Code สำหรับการชำระเงิน

        ฟังก์ชันนี้จะ:
        - ตรวจสอบ session และดึง user_id
        - ตรวจสอบว่ามีคำสั่งซื้อล่าสุดที่สถานะเป็น "waiting" หรือไม่
        - ตรวจสอบว่ามีสินค้าภายในตะกร้าหรือยัง
        - อัปเดตสถานะคำสั่งซื้อเป็น "pending"
        - สร้างข้อความสรุปรายการสินค้า
        - สร้าง QR Code สำหรับชำระเงินผ่าน PromptPay

        ใช้กรณีที่ลูกค้าถาม:
        - "ต้องโอนเงินยังไง?"
        - "ขอดู QR Code จ่ายเงิน"
        - "เช็กเอาตะกร้าไปจ่ายเลย"
        - "ขอ checkout เลยครับ"

        Args:
            session_id (int | None): รหัส session ของผู้ใช้

        Returns:
            dict:
                - status (str): สถานะของคำสั่ง ("success", "fail")
                - detail (str): ข้อความอธิบายผลลัพธ์
                - cart_summary (str, optional): สรุปรายการสินค้าในคำสั่งซื้อ
                - qr_base64 (str, optional): รูปภาพ QR แบบ base64 สำหรับการชำระเงิน
                - payment_info (str, optional): ข้อความอธิบายการโอนเงิน
        """

        return checkout_cart(supabase, session_id)

    # Decode slip and verify
    @mcp.tool(name="decode_slip_and_verify", description="ตรวจสอบสลิปและยืนยันการชำระเงิน")
    @log_function_call
    def mcp_decode_slip_and_verify(full_save_path: str, session_id: int | None = None) -> dict:
        """
        ถอดรหัสรูปสลิปและตรวจสอบการชำระเงิน

        ฟังก์ชันนี้จะ:
        - ตรวจสอบ session และดึง user_id
        - ถอดรหัสสลิปเพื่อดึงหมายเลขอ้างอิง (ref_nbr)
        - ตรวจสอบว่า ref_nbr ถูกใช้ไปแล้วหรือไม่
        - ดึง order ล่าสุดของผู้ใช้
        - เรียก verify_slip() เพื่อตรวจสอบ ref_nbr กับยอดเงิน
        - ถ้ายืนยันสำเร็จ จะอัปเดต ref_nbr ลงใน order

        ใช้กรณีที่ลูกค้าถามหรือส่งหลักฐาน เช่น:
        - "โอนเงินแล้วนะครับ"
        - "นี่สลิปการชำระเงิน"
        - "อัปโหลดสลิปให้แล้ว ตรวจสอบให้หน่อย"
        - "จ่ายแล้วช่วยเช็กที"

        Args:
            slip_base64 (str): ข้อมูลรูปภาพสลิปแบบ base64
            session_id (int | None): รหัส session ของผู้ใช้

        Returns:
            dict:
                - ref_nbr (str | None): หมายเลขอ้างอิงจากสลิป (ถ้า decode สำเร็จ)
                - status (str): "success", "error" หรือ "fail"
                - message (str): ข้อความสรุปผลการตรวจสอบ
        """

        return decode_slip_and_verify(supabase, full_save_path, session_id)

    # Cancel latest order
    @mcp.tool(name="cancel_lastest_order", description="ยกเลิกคำสั่งซื้อล่าสุดของผู้ใช้")
    @log_function_call
    def mcp_cancel_lastest_order(session_id: int | None = None) -> dict:
        """
        ยกเลิกคำสั่งซื้อล่าสุดของผู้ใช้ หากยังอยู่ในสถานะที่สามารถยกเลิกได้

        ฟังก์ชันนี้จะ:
        - ตรวจสอบ session และดึง user_id
        - ดึงคำสั่งซื้อล่าสุดของผู้ใช้
        - ตรวจสอบว่าสถานะคำสั่งซื้อนั้นอยู่ในสถานะที่สามารถยกเลิกได้ (waiting, pending)
        - อัปเดตสถานะคำสั่งซื้อเป็น "cancelled"

        ใช้กรณีที่ลูกค้าพูดว่า:
        - "ยกเลิกออเดอร์ได้ไหม"
        - "เปลี่ยนใจ ไม่เอาแล้วครับ"
        - "ลบคำสั่งซื้อล่าสุดให้หน่อย"
        - "ของในตะกร้าผิด ขอเริ่มใหม่"

        Args:
            session_id (int | None): รหัส session ของผู้ใช้

        Returns:
            dict:
                - status (str): "success" หรือ "fail"
                - detail (str): ข้อความอธิบายผลการดำเนินการ
                - cancelled_total (float, optional): ยอดรวมของคำสั่งซื้อที่ถูกยกเลิก (ถ้าสำเร็จ)
        """

        return cancel_lastest_order(supabase, session_id)

    # Remove product from cart
    @mcp.tool(name="remove_product_from_cart", description="นำสินค้าออกจากตะกร้าสินค้า")
    @log_function_call
    def mcp_remove_product_from_cart(product_name: str, session_id: int | None = None) -> dict:
        """
        ลบสินค้าที่ระบุออกจากตะกร้าของผู้ใช้ และอัปเดตราคารวมใหม่

        ฟังก์ชันนี้จะ:
        - ตรวจสอบ session และดึง user_id
        - ดึงคำสั่งซื้อล่าสุดของผู้ใช้ที่อยู่ในสถานะ "waiting"
        - ตรวจสอบว่าสินค้าที่ต้องการลบมีอยู่ในระบบหรือไม่
        - ลบสินค้านั้นออกจากคำสั่งซื้อ (order_items)
        - คำนวณยอดรวมใหม่ของตะกร้า และอัปเดตกลับไปยัง order
        - คืนข้อความสรุปรายการสินค้าในตะกร้าล่าสุด

        Args:
            product_name (str): ชื่อสินค้าที่ต้องการลบ
            session_id (int | None): รหัส session ของผู้ใช้

        ใช้กรณีที่ลูกค้าพูดว่า:
            - "เอา Dixit ออก"
            - "ไม่เอา Codenames แล้ว"
            - "ลบสินค้าอันนี้ออกจากตะกร้าให้หน่อย"
            - "ใส่ผิด ขอเอา Root ออก"

        Returns:
            dict:
                - status (str): "success", "fail"
                - detail (str): ข้อความอธิบายผลลัพธ์
                - cart_summary (str, optional): รายการสินค้าในตะกร้าที่อัปเดตแล้ว
        """

        return remove_product_from_cart(supabase, product_name, session_id)

    # Reactivate lastest order
    @mcp.tool(name="reactivate_lastest_order", description="นำคำสั่งซื้อที่ถูกยกเลิกกลับมาใช้งาน")
    @log_function_call
    def mcp_reactivate_lastest_order(session_id: int | None = None) -> dict:
        """
        นำคำสั่งซื้อล่าสุดที่ถูกยกเลิก (cancelled) กลับมาใช้งานใหม่อีกครั้ง

        ฟังก์ชันนี้จะ:
        - ตรวจสอบ session และดึง user_id
        - ดึงคำสั่งซื้อล่าสุดของผู้ใช้
        - ตรวจสอบว่าสถานะคำสั่งซื้อต้องเป็น "cancelled"
        - ตรวจสอบว่าคำสั่งซื้อนั้นมีสินค้าอยู่
        - คำนวณยอดรวมใหม่จากราคาสินค้าปัจจุบัน
        - อัปเดตสถานะเป็น "waiting" และบันทึกยอดรวมใหม่
        - สร้างข้อความสรุปรายการสินค้าในคำสั่งซื้อ

        ใช้กรณีที่ลูกค้าพูดว่า:
        - "เมื่อกี้เผลอยกเลิกไป ขอเอากลับมา"
        - "เมื่อวานกดยกเลิกไป ขอใช้คำสั่งเดิมได้ไหม"
        - "อยากกลับไปใช้ออเดอร์ที่เพิ่งลบ"
        - "สั่งของใหม่ไม่สะดวก ขอใช้ของเก่า"

        Args:
            session_id (int | None): รหัส session ของผู้ใช้

        Returns:
            dict:
                - status (str): "success" หรือ "fail"
                - detail (str): ข้อความสรุปผลการดำเนินการ
                - cart_summary (str, optional): รายการสินค้าและราคารวมล่าสุดของคำสั่งซื้อ
        """

        return reactivate_lastest_order(supabase, session_id)

    # Cart summary
    @mcp.tool(name="cart_summary", description="แสดงรายการสินค้าในตะกร้าสินค้าล่าสุด")
    @log_function_call
    def mcp_cart_summary(session_id: int | None = None) -> dict:
        """
        แสดงสรุปรายการสินค้าในคำสั่งซื้อล่าสุดของผู้ใช้ (เฉพาะสถานะ waiting หรือ pending)

        ฟังก์ชันนี้จะ:
        - ตรวจสอบ session และดึง user_id
        - ดึงคำสั่งซื้อล่าสุดของผู้ใช้
        - ตรวจสอบว่าสถานะต้องเป็น "waiting" หรือ "pending"
        - สร้างข้อความสรุปรายการสินค้า (ชื่อ, จำนวน, ราคา, รวมทั้งหมด)

        ใช้กรณีที่ลูกค้าถามว่า:
        - "ในตะกร้ามีอะไรบ้าง"
        - "ช่วยสรุปคำสั่งซื้อให้หน่อย"
        - "อยากดูว่าใส่อะไรไปแล้ว"
        - "เช็กตะกร้าให้หน่อยครับ"

        Args:
            session_id (int | None): รหัส session ของผู้ใช้

        Returns:
            dict:
                - status (str): "success" หรือ "fail"
                - detail (str): ข้อความอธิบายผลลัพธ์
                - cart_summary (str, optional): รายการสินค้าและราคารวมในตะกร้า (ถ้าสำเร็จ)
        """

        return cart_summary(supabase, session_id)

    return mcp


# if __name__ == "__main__":
mcp = FastMCP(
    name="generative-saleman-payment-cart-managment",
    dependencies=["supabase", "dotenv"],
    description="A tool that manages product cart, checkout, payment verification, and order lifecycle for boardgame sales.",
    version="0.0.1",
    instructions="""
    คุณคือผู้ช่วยจัดการรถเข็นของร้านขายบอร์ดเกมออนไลน์
    - แต่ถ้าผู้ใช้พยายามทำรายการ เช่น "เพิ่ม Root 2 กล่อง", "Checkout", "ยกเลิกออเดอร์", "แนบสลิป" → ต้องมี session_id ก่อน
    - ถ้ายังไม่มี session_id (ดูจากผลลัพธ์ที่ส่งกลับว่าเป็นข้อความ "กรุณาใส่ข้อมูลชื่อ และ Phone number มาก่อนทำรายการครับ") → ให้ถามชื่อและเบอร์โทรผู้ใช้ แล้วเรียก `get_session_id(name, phone)` ใน generative-saleman-product-info
    - หลังจากได้ session_id แล้วให้เก็บ session_id ไว้ และใส่ในทุกคำสั่งที่เกี่ยวกับการสั่งซื้อ
    ห้ามสร้าง session ใหม่เองโดยพลการ ต้องรอให้ผู้ใช้ให้ชื่อและเบอร์โทรก่อน
    """,
)
mcp = register(mcp)
mcp.run()
