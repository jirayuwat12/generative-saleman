import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("/Users/jirayuwat/Desktop/generative-saleman/.env", override=True)
# load_dotenv(find_dotenv(), override=True)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
if SUPABASE_URL is None:
    raise ValueError("SUPABASE_URL environment variable is not set.")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if SUPABASE_KEY is None:
    raise ValueError("SUPABASE_KEY environment variable is not set.")
QR_VERIFY_TOKEN = os.getenv("QR_VERIFY_TOKEN")
if QR_VERIFY_TOKEN is None:
    raise ValueError("QR_VERIFY_TOKEN environment variable is not set.")
