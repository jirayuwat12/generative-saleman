import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

# Initialize Supabase client
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
QR_VERIFY_TOKEN: str = os.getenv("QR_VERIFY_TOKEN", "")
