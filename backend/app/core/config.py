from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Full-Stack SaaS Dashboard"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dashboard"

    class Config:
        env_file = ".env"

settings = Settings()
