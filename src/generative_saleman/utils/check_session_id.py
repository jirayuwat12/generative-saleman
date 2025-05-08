from supabase import Client
from generative_saleman.services.db_services.user_db import get_user_id_from_session_id


def check_session_id(supabase: Client, session_id: int | None):
    if session_id is None:
        return {"status": "fail", "detail": "กรุณาใส่ข้อมูลชื่อ และ Phone number มาก่อนทำรายการครับ"}

    user_id = get_user_id_from_session_id(supabase, session_id)
    if user_id is None:
        return {"status": "fail", "detail": "session_id ไม่ถูกต้อง กรุณาใส่ข้อมูลชื่อ และ Phone number มาอีกครั้งครับ"}
    else:
        return user_id
