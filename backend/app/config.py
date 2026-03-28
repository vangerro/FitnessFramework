from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    # Ignore keys like POSTGRES_* in backend/.env (used by Docker Compose root .env only).
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()

