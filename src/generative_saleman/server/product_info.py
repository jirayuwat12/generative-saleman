from generative_saleman.handler.user import get_session_id
from generative_saleman.services.db_services.base import get_supabase_client
from mcp.server.fastmcp import FastMCP

from generative_saleman.services.db_services.products_db import get_all_products, get_product_by_name
from functools import wraps

from generative_saleman.utils.get_log import get_log

log = get_log("_product_info.py")


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

    @mcp.tool("get_all_product_info", description="ดึงข้อมูลสินค้าทั้งหมดในระบบ ตาม page และ nrow")
    @log_function_call
    def mcp_get_available_products(page: int = 1, nrow: int = 10) -> list[str]:
        """
        ดึงข้อมูลสินค้าทั้งหมดที่มีในระบบ (จำนวนสินค้าคงเหลือ > 0) แบบแบ่งหน้า และคืนข้อความสรุปของสินค้าแต่ละรายการ

        ฟังก์ชันนี้จะ:
        - ดึงรายการสินค้าจากฐานข้อมูลตามจำนวนที่กำหนด (`page`, `nrow`)
        - ตรวจสอบว่าแต่ละสินค้ามี `amount > 0` หรือไม่
        - คืนค่าข้อความสรุปข้อมูลของแต่ละสินค้าด้วยเมธอด `format_product()` เช่น ชื่อ, ราคา, คงเหลือ

        ใช้ฟังก์ชันนี้เมื่อ:
        - ผู้ใช้ถามว่า "มีอะไรขายบ้าง"
        - ผู้ใช้ต้องการดูสินค้าทั้งหมด
        - ต้องการดึงรายการสินค้าพร้อมข้อมูลประกอบแบบสั้น ๆ

        Args:
            page (int): หน้าเริ่มต้นของรายการ (default = 1)
            nrow (int): จำนวนรายการต่อหน้า (default = 10)

        Returns:
            list[str]: รายการข้อความสรุปของสินค้าที่มีอยู่ในคลัง
        """
        products = get_all_products(supabase, page, nrow)
        return [product.format_product() for product in products if product.amount > 0]

    @mcp.tool(name="get_production_info", description="ดึงข้อมูลสินค้า ทั้งที่มีอยู่ในระบบและไม่มีในระบบ")
    @log_function_call
    def mcp_get_production_info(product_name: str) -> str:
        """
        ตรวจสอบข้อมูลสินค้าจากชื่อ และคืนข้อความสรุปข้อมูลของสินค้า

        ฟังก์ชันนี้จะ:
        - ค้นหาสินค้าจากฐานข้อมูลด้วยชื่อที่ให้มา
        - ถ้าไม่พบสินค้า จะคืนข้อความว่า "ไม่พบข้อมูลสินค้า"
        - ถ้าพบสินค้า จะเรียกใช้เมธอด `format_product()` เพื่อแสดงข้อมูลสินค้าในรูปแบบที่เหมาะสม เช่น
        ชื่อสินค้า ราคา คงเหลือ รายละเอียด ฯลฯ

        สามารถใช้ฟังก์ชันนี้ในกรณีที่ลูกค้าถามว่า:
        - "มีขายไหม"
        - "เหลืออยู่กี่ชิ้น"
        - "ราคาสินค้านี้เท่าไร"
        - หรือเพื่อแสดงรายละเอียดโดยรวมของสินค้า

        Args:
            product_name (str): ชื่อของสินค้าที่ต้องการตรวจสอบ

        Returns:
            str: ข้อความสรุปข้อมูลของสินค้า หรือแจ้งว่าไม่พบสินค้า
        """
        product = get_product_by_name(supabase, product_name)
        if product is None:
            return "ไม่พบข้อมูลสินค้า"
        elif product.amount == 0:
            return "สินค้าหมด"
        else:
            return product.format_product()

    @mcp.tool(name="get_session_id", description="รับค่า session_id จากชื่อผู้ใช้และเบอร์โทรศัพท์")
    @log_function_call
    def mcp_get_session_id(name: str, phone: str) -> dict:
        """
        สร้าง session ใหม่จากชื่อและเบอร์โทรของผู้ใช้

        ฟังก์ชันนี้จะ:
        - ตรวจสอบว่ามีชื่อหรือเบอร์โทรนี้อยู่ในระบบหรือไม่
        - ถ้ามีแล้ว → ตรวจสอบว่าข้อมูลตรงกันหรือไม่ (ชื่อ/เบอร์ต้อง match กันทั้งคู่)
        - ถ้าไม่ตรงกัน → แจ้ง error ว่าชื่อหรือเบอร์ถูกใช้แล้ว
        - ถ้ายังไม่เคยมี → สร้างผู้ใช้ใหม่ในระบบ
        - สุดท้ายสร้าง session และคืน session_id กลับมา

        ใช้เมื่อ:
        - ผู้ใช้เริ่มต้นกระบวนการสั่งซื้อ แต่ยังไม่มี session
        - ต้องการระบุตัวตนของลูกค้าเพื่อเชื่อมโยงกับคำสั่งซื้อในระบบ

        Args:
            name (str): ชื่อของผู้ใช้
            phone (str): เบอร์โทรศัพท์ของผู้ใช้ เช่น "0812345678" หรือ "+66812345678" หรือ "081-2345678" หรือ "081-234-5678"

        Returns:
            dict:
                - status (str): "success" หรือ "fail"
                - detail (str): ข้อความสรุปผลลัพธ์
                - session_id (int, optional): รหัส session ที่สร้างใหม่ (หากสำเร็จ)
        """
        return get_session_id(supabase, name, phone)

    return mcp


if __name__ == "__main__":
    mcp = FastMCP(
        name="generative-saleman-product-info",
        dependencies=["supabase", "dotenv"],
        description="A tool to get all product avaliable and product-info",
        version="0.0.1",
        instructions="""
        คุณคือผู้ช่วยตอบคำถามเกี่ยวกับสินค้า เช่น ราคาหรือจำนวนคงเหลือ
        - คำถามเหล่านี้ไม่จำเป็นต้องมี session_id
        - แต่ถ้าผู้ใช้จะเริ่มสั่งซื้อ ให้ถามชื่อและเบอร์โทร แล้วเรียก get_session_id(name, phone)
        - เมื่อได้ session_id แล้วให้ส่งต่อให้ระบบ cart
        """,
    )
    mcp = register(mcp)
    mcp.run()
