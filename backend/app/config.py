from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Docker içinde bu URL'ler farklı
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://pdfai_user:pdfai_password123@localhost:5432/pdfai_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # JWT için secret key
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-please")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()