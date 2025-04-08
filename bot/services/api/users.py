import httpx

from environs import Env
from config.config import get_settings

config = get_settings()


class api_users:
    @staticmethod
    async def register_user(telegram_id: str, username: str):
        payload = {
            "telegram_id": telegram_id,
            "username": username
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{config.api_base_url}users/", json=payload)
            response.raise_for_status()
            return response.json()
