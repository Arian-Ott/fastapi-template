from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"  # fallback for tests
    API_PREFIX: str = "/api"

    model_config = ConfigDict(env_file=".env")


settings = Settings()