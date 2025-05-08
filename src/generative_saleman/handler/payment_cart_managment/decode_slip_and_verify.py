import base64
from supabase import Client
from generative_saleman.services.db_services.orders_db import (
    get_lastest_order_by_user_id,
    is_ref_already_used,
    update_order_qr_reference,
)
from generative_saleman.utils.check_session_id import check_session_id
from generative_saleman.services.qr_services import decode_slip, verify_slip


def decode_slip_and_verify(supabase: Client, full_save_path: str, session_id: int | None) -> dict:
    res = check_session_id(supabase, session_id)
    if not isinstance(res, int):
        return res
    user_id = res

    # read image from full_save_path to slip_base64
    with open(full_save_path, "rb") as f:
        data = f.read()
        slip_base64 = base64.b64encode(data).decode("utf-8")

    ref_nbr = decode_slip(slip_base64)
    if ref_nbr is None:
        return {"ref_nbr": None, "status": "error", "message": "Invalid slip image."}

    if is_ref_already_used(supabase, ref_nbr):
        return {"ref_nbr": ref_nbr, "status": "error", "message": "This slip has already been used."}

    order = get_lastest_order_by_user_id(supabase, user_id)
    if order is None:
        return {"ref_nbr": ref_nbr, "status": "error", "message": "No order found."}

    try:
        response = verify_slip(ref_nbr=ref_nbr, amount=str(order.total_amount))
        if response["success"]:
            update_order_qr_reference(supabase, order.id, ref_nbr)
        return {
            "ref_nbr": ref_nbr,
            "status": "success" if response["success"] else "error",
            "message": "Slip verification Success." if response["success"] else "Slip verification Success.",
        }
    except Exception as e:
        return {"ref_nbr": ref_nbr, "status": "error", "message": str(e)}
