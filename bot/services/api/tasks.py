import logging
from typing import Optional

import httpx

from environs import Env

env = Env()
env.read_env()

BASE_URL = env("API_BASE_URL")


async def update_task_status(task_id: str,
                             is_completed: bool) -> bool:
    payload = {
        "is_completed": is_completed
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f'{BASE_URL}tasks/{task_id}/', json=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            return False


async def update_task_description(task_id: str,
                                  new_description: str) -> bool:
    payload = {
        "description": new_description
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(f'{BASE_URL}tasks/{task_id}/', json=payload)
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            return False


async def get_tasks(telegram_id: str) -> list:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'{BASE_URL}tasks/', params={"user_id": telegram_id})
            response.raise_for_status()
            logging.Logger("s").critical(response.json())
            return response.json()
        except httpx.HTTPError as e:
            return []


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
        response = await client.post(f'{BASE_URL}tasks/', json=payload)
        response.raise_for_status()
        return response.json()


async def delete_task(task_id: str) -> bool:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f'{BASE_URL}tasks/{task_id}/')
        return response.status_code == 204
