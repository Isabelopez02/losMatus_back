import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-me")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")

settings = Settings()
