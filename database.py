
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase

    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SECRET_KEY")

        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SECRET_KEY must be configured"
            )

        _supabase = create_client(url, key)

    return _supabase


def create_database():
    # Supabase table is created in the Supabase dashboard.
    # This function verifies that the connection settings exist.
    get_supabase()


def save_record(
    message, intent, risk_profile, priority, summary, input_tokens
):
    supabase = get_supabase()

    result = supabase.table("ingestion_records").insert({
        "message": message,
        "intent": intent,
        "risk_level": risk_profile,
        "priority": priority,
        "summary": summary,
        "input_tokens": input_tokens,
    }).execute()

    return result


if __name__ == "__main__":
    create_database()
    print("Supabase connection configured successfully!")

