from supabase import Client
from src.generative_saleman.model.user import User, UserCreate


def get_user_by_name(supabase: Client, name: str) -> User:
    result = supabase.table("users").select("*").eq("name", name).single().execute()
    data = result.data
    return User(**data)


def get_user_by_id(supabase: Client, user_id: str) -> User:
    result = supabase.table("users").select("*").eq("id", user_id).single().execute()
    data = result.data
    return User(**data)


def create_user(supabase: Client, user_create: UserCreate) -> User:
    result = supabase.table("users").insert(user_create.model_dump(exclude_unset=True)).execute()
    data = result.data[0]
    return User(**data)


def update_user(supabase: Client, user_id: str, user_update: dict) -> User:
    result = supabase.table("users").update(user_update).eq("id", user_id).execute()
    data = result.data[0]
    return User(**data)
