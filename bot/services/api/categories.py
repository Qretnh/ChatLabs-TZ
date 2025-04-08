from typing import Union

import httpx

from config.config import get_settings

config = get_settings()


class api_categories:

    @staticmethod
    async def get_categories(telegram_id: Union[str, int]) -> list:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'{config.api_base_url}categories/', params={"user_id": telegram_id})
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                return []

    @staticmethod
    async def create_category(name: str, user_id: int) -> dict:
        payload = {
            "name": name,
            "user_id": user_id
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{config.api_base_url}categories/', json=payload)
            if response.status_code != 201:
                response.raise_for_status()
            return response.json()

    @staticmethod
    async def delete_category(category_id: str, user_id: int) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f'{config.api_base_url}categories/{category_id}/',
                                           params={"user_id": user_id})
            return response.status_code == 204
