from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    model_config = ConfigDict(env_file=".env")

settings = Settings()

