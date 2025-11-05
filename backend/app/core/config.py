from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Full-Stack SaaS Dashboard"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dashboard"
    
    # JWT Settings (loaded from .env)
    JWT_SECRET: str = "your-secret-key-change-in-production-use-env-var"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
