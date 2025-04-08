import logging
from typing import Optional

import httpx
from config.config import get_settings

config = get_settings()


class api_tasks:
    @staticmethod
    async def update_task_status(task_id: str,
                                 is_completed: bool) -> bool:
        payload = {
            "is_completed": is_completed
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(f'{config.api_base_url}tasks/{task_id}/', json=payload)
                response.raise_for_status()
                return True
            except httpx.HTTPError as e:
                return False

    @staticmethod
    async def update_task_description(task_id: str,
                                      new_description: str) -> bool:
        payload = {
            "description": new_description
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.patch(f'{config.api_base_url}tasks/{task_id}/', json=payload)
                response.raise_for_status()
                return True
            except httpx.HTTPError as e:
                return False

    @staticmethod
    async def get_tasks(telegram_id: str) -> list:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'{config.api_base_url}tasks/', params={"user_id": telegram_id})
                response.raise_for_status()
                logging.Logger("s").critical(response.json())
                return response.json()
            except httpx.HTTPError as e:
                return []

    @staticmethod
    async def create_task(
            telegram_id: str,
            title: str,
            category_id: Optional[str] = None,
            description: str = "",
            due_date: Optional[str] = None,  # Ожидаем строку вида '2025-03-24'
            due_time: Optional[str] = None  # Ожидаем строку вида '18:00' или None
    ) -> dict:
        payload = {
            "telegram_id": str(telegram_id),
            "title": title,
            "description": description,
            "due_date": due_date,
            "due_time": due_time if due_time else "18:00",  # Если время не передано - ставим 18:00
        }

        if category_id:
            payload["category_id"] = category_id

        async with httpx.AsyncClient() as client:
            response = await client.post(f'{config.api_base_url}tasks/', json=payload)
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def delete_task(task_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f'{config.api_base_url}tasks/{task_id}/')
            return response.status_code == 204
