from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Full-Stack SaaS Dashboard"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dashboard"
    
    # JWT Settings (loaded from .env)
    JWT_SECRET: str = "your-secret-key-change-in-production-use-env-var"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email Settings (Resend API)
    RESEND_API_KEY: Optional[str] = None
    MAIL_FROM: str = "noreply@adamobrien.dev"  # Use verified domain
    MAIL_FROM_NAME: str = "SaaS Dashboard"
    
    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    AVATAR_DIR: str = "uploads/avatars"
    MAX_AVATAR_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env that aren't in Settings

settings = Settings()
