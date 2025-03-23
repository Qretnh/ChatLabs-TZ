import logging

import httpx

from environs import Env

env = Env()
env.read_env()

BASE_URL = env("API_BASE_URL")


async def get_categories(telegram_id: str) -> list:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'{BASE_URL}categories/', params={"user_id": telegram_id})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"Ошибка при получении категорий: {e}")
            return []

async def create_category(name: str, user_id: int) -> dict:
    payload = {
        "name": name,
        "user_id": user_id
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f'{BASE_URL}categories/', json=payload)
        if response.status_code != 201:
            print(f"Ошибка создания категории: {response.text}")
            response.raise_for_status()
        return response.json()


async def delete_category(category_id: str, user_id: int) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f'{BASE_URL}categories/{category_id}/', params={"user_id": user_id})
        return response.status_code == 204

