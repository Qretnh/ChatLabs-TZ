import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from aiogram_dialog import setup_dialogs

import logging

from handlers.menu import router as menu

from dialogs.dialog import tasks_dialog

from config.config import get_settings

config = get_settings()

bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def main():
    dp = Dispatcher()

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    dp.include_router(menu)
    dp.include_router(tasks_dialog)

    setup_dialogs(dp)

    await bot.set_my_commands([BotCommand(command='start', description="Стартовое меню")])
    await bot.delete_webhook(drop_pending_updates=True)  # удаление апдейтов до запуска бота
    await dp.start_polling(bot)  # запуск бота!


if __name__ == '__main__':
    asyncio.run(main())
