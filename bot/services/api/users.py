import httpx

from environs import Env

env = Env()
env.read_env()

BASE_URL = env("API_BASE_URL")

async def register_user(telegram_id: str, username: str):
    payload = {
        "telegram_id": telegram_id,
        "username": username
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}users/", json=payload)
        response.raise_for_status()
        return response.json()
