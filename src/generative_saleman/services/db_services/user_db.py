from typing import Optional
from supabase import Client
from generative_saleman.model.user import User, UserCreate
from generative_saleman.utils.get_log import get_log

log = get_log("user_db")


def get_user_by_name(supabase: Client, name: str) -> User | None:
    result = supabase.table("users").select("*").eq("name", name).limit(1).execute()
    data = result.data
    if data:
        return User(**data[0])
    else:
        return None


def get_user_by_id(supabase: Client, user_id: str) -> User | None:
    result = supabase.table("users").select("*").eq("id", user_id).limit(1).execute()
    data = result.data
    if data:
        return User(**data[0])
    else:
        return None


def get_user_by_phone(supabase: Client, phone: str):
    response = supabase.table("users").select("*").eq("phone", phone).limit(1).execute()
    return User(**response.data[0]) if response.data else None


def get_user_id_from_session_id(supabase: Client, session_id: int) -> Optional[int]:
    result = supabase.table("session").select("user_id").eq("id", session_id).limit(1).execute()
    return result.data[0].get("user_id") if result.data else None


def create_user(supabase: Client, user_create: UserCreate) -> User:
    log.info(user_create.model_dump(exclude={"id"}))
    result = supabase.table("users").insert(user_create.model_dump(exclude={"id"})).execute()
    data = result.data[0]
    return User(**data)


def update_user(supabase: Client, user_id: str, user_update: dict) -> User:
    result = supabase.table("users").update(user_update).eq("id", user_id).execute()
    data = result.data[0]
    return User(**data)
