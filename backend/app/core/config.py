from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Syncraft API"
    app_env: str = "development"
    database_url: str = "sqlite:///./syncraft.db"
    frontend_origin: str = "http://localhost:5173"
    jwt_secret: str = "dev-only-change-me"
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    demo_email: str = "demo@syncraft.dev"
    demo_password: str = "Syncraft123!"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
