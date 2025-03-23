import requests
import logging
from environs import Env

env = Env()
env.read_env()

logger = logging.getLogger(__name__)

def send_notification(task):
    BOT_TOKEN = env("BOT_TOKEN")

    user_id = task.user.telegram_id
    message_text = ("🔔 Напоминание!\n"
                    f"Задача: {task.title}\n"
                    f"Описание: {task.description}\n")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": user_id,
        "text": message_text,
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        logger.info("Сообщение успешно отправлено!")
        return 1
    else:
        logger.error(f"Ошибка: {response.status_code}, {response.text}")
        return 0
