from supabase import Client

from generative_saleman.model.session import SessionCreate
from generative_saleman.model.user import UserCreate
from generative_saleman.services.db_services.session_db import create_session
from generative_saleman.services.db_services.user_db import (
    create_user,
    get_user_by_name,
    get_user_by_phone,
)


def get_session_id(supabase: Client, name: str, phone: str) -> dict:
    phone = phone.replace("-", "").replace(" ", "")
    user_by_name = get_user_by_name(supabase, name)
    user_by_phone = get_user_by_phone(supabase, phone)

    if user_by_name and user_by_name.phone != phone:
        return {"status": "fail", "detail": "ชื่อนี้ถูกใช้แล้วกับเบอร์อื่น"}
    if user_by_phone and user_by_phone.name != name:
        return {"status": "fail", "detail": "เบอร์โทรนี้ถูกใช้แล้วกับชื่ออื่น"}

    # ถ้ามี user อยู่แล้วจาก name หรือ phone → ใช้อันนั้น
    user = user_by_name or user_by_phone

    # ถ้ายังไม่เจอเลย → สร้างใหม่
    if not user:
        user_create = UserCreate(name=name, phone=phone)
        user = create_user(supabase, user_create)

    # สร้าง session
    session = create_session(supabase, SessionCreate(user_id=user.id))

    return {
        "status": "success",
        "detail": f"สร้าง session สำหรับ {name} เรียบร้อยแล้ว",
        "session_id": session.id,
    }
