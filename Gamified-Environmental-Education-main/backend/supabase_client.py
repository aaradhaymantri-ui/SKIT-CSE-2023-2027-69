"""
supabase_client.py
Helper module to initialize and expose the official Supabase Python client.
"""
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

supabase = None

# Only initialize client if valid non-placeholder credentials are provided
if (
    SUPABASE_URL
    and SUPABASE_KEY
    and "your-project-id" not in SUPABASE_URL
    and "your-anon" not in SUPABASE_KEY
):
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[*] Supabase Python client initialized successfully.")
    except ImportError:
        print("[*] 'supabase' package is not installed. Run: pip install supabase")
    except Exception as e:
        print(f"[*] Supabase client initialization notice: {e}")


def get_supabase():
    """Returns the initialized Supabase client instance or None."""
    return supabase
