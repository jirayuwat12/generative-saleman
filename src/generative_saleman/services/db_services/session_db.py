from typing import Optional
from supabase import Client
from generative_saleman.model.session import Session, SessionCreate
from generative_saleman.utils.get_log import get_log


def get_session_by_id(supabase: Client, session_id: int) -> Optional[Session]:
    result = supabase.table("session").select("*").eq("id", session_id).limit(1).execute()
    data = result.data
    if data:
        return Session(**data[0])
    return None


def create_session(supabase: Client, session_create: SessionCreate) -> Session:
    log = get_log("session_create.model_dump()")
    log.info(session_create.model_dump())
    result = supabase.table("session").insert(session_create.model_dump()).execute()
    data = result.data[0]
    return Session(**data)


def update_session(supabase: Client, session_id: int, session_update: dict) -> Session:
    result = supabase.table("session").update(session_update).eq("id", session_id).execute()
    data = result.data[0]
    return Session(**data)


def deactivate_all_sessions_by_user(supabase: Client, user_id: int) -> None:
    supabase.table("session").update({"is_active": False}).eq("user_id", user_id).execute()
