from supabase import create_client, Client
from generative_saleman.config import SUPABASE_URL, SUPABASE_KEY


_supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase_client() -> Client:
    return _supabase
