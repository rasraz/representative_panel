import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    DEBUG: bool = os.getenv("DEBUG")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
    ALLOWED_ORIGINS = allowed_origins.split(",") if allowed_origins else ["*"]

settings = Settings()