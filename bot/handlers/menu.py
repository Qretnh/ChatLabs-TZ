import aiogram_dialog
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from FSM import FSMTodoList

from services.api.users import api_users

router = Router()

@router.message(Command(commands=['start']))
async def menu(message: Message, dialog_manager: DialogManager):
    await api_users.register_user(str(message.from_user.id), message.from_user.username)
    await dialog_manager.start(FSMTodoList.start, data={"user_id": message.from_user.id})
