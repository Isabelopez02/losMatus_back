import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-me")
    
    # Supabase y otras URLs pueden incluir ?pgbouncer=true, lo cual rompe psycopg2
    _raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./database.db")
    if "?pgbouncer=true" in _raw_db_url:
        _raw_db_url = _raw_db_url.replace("?pgbouncer=true", "")
    elif "&pgbouncer=true" in _raw_db_url:
        _raw_db_url = _raw_db_url.replace("&pgbouncer=true", "")
        
    DATABASE_URL: str = _raw_db_url

    # URL base del propio backend (usada por el bot de Telegram)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000/api")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # IA (Groq — compatible con la API de OpenAI)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

settings = Settings()
