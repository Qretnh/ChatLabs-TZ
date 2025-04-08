from functools import lru_cache

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    bot_token: str
    api_base_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()