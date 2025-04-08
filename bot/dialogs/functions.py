import datetime

from aiogram.types import Message, CallbackQuery

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from datetime import date

from FSM import FSMTodoList

from services.api.tasks import api_tasks
from services.api.categories import api_categories

from environs import Env

env = Env()
env.read_env()

BASE_URL = env("API_BASE_URL")

DEFAULT_TIME = "18:00"


async def on_time_entered(message: Message,
                          widget: ManagedTextInput,
                          dialog_manager: DialogManager,
                          text: str):
    try:
        datetime.datetime.strptime(text, "%H:%M")
    except ValueError:
        await message.answer("❌ Неверный формат времени. Введите в формате HH:MM (например, 18:00)")
        return

    dialog_manager.dialog_data["due_time"] = text
    await dialog_manager.next()


async def on_skip_time(callback: CallbackQuery,
                       button: Button,
                       dialog_manager: DialogManager):
    dialog_manager.dialog_data["due_time"] = DEFAULT_TIME
    await dialog_manager.next()


async def on_no_description(callback: CallbackQuery,
                            button: Button,
                            dialog_manager: DialogManager):
    dialog_manager.dialog_data["description"] = "Нету"
    await dialog_manager.next()


async def view_task_detail(callback: CallbackQuery,
                           widget: Select,
                           dialog_manager: DialogManager,
                           item_id: str):
    dialog_manager.dialog_data['task_id'] = item_id

    all_tasks = [task for tasks in dialog_manager.dialog_data['TODO'].values() for task in tasks]
    task = next((task for task in all_tasks if task['id'] == item_id), None)
    dialog_manager.dialog_data['task'] = task

    await dialog_manager.switch_to(FSMTodoList.task_detail)


async def view_task_archive(callback: CallbackQuery,
                            widget: Select,
                            dialog_manager: DialogManager,
                            item_id: str):
    dialog_manager.dialog_data['task_id'] = item_id

    all_tasks = dialog_manager.dialog_data['archive_tasks']
    task = next((task for task in all_tasks if task['id'] == item_id), None)
    dialog_manager.dialog_data['task'] = task

    await dialog_manager.switch_to(FSMTodoList.archive_task_detail)


async def delete_task_handler(callback: CallbackQuery, button: Button,
                              dialog_manager: DialogManager):
    await api_tasks.delete_task(dialog_manager.dialog_data['task_id'])
    await dialog_manager.switch_to(FSMTodoList.tasks_by_category)


async def complete_task_handler(callback: CallbackQuery, button: Button,
                                dialog_manager: DialogManager):
    await api_tasks.update_task_status(dialog_manager.dialog_data['task_id'], True)
    await dialog_manager.switch_to(FSMTodoList.tasks_by_category)


async def delete_category_handler(callback: CallbackQuery,
                                  widget: Select,
                                  dialog_manager: DialogManager,
                                  item_id: str):
    telegram_id = str(callback.from_user.id)

    # Получаем все задачи пользователя
    tasks = await api_tasks.get_tasks(telegram_id)
    tasks_in_category = [task for task in tasks if str(task["category"]['id']) == str(item_id)]

    if tasks_in_category:
        await callback.answer("Нельзя удалить категорию — в ней есть задачи!", show_alert=True)
        return

    success = await api_categories.delete_category(item_id, callback.from_user.id)
    if success:
        await callback.answer("Категория удалена")
    else:
        await callback.answer("Ошибка удаления категории", show_alert=True)


async def on_description_entered(message: Message,
                                 widget: ManagedTextInput,
                                 dialog_manager: DialogManager,
                                 text: str):
    task = dialog_manager.dialog_data['task']
    task['description'] = text
    await api_tasks.update_task_description(task['id'], text)
    await dialog_manager.switch_to(FSMTodoList.task_detail)


async def on_description_updated(message: Message,
                                 widget: ManagedTextInput,
                                 dialog_manager: DialogManager,
                                 text: str):
    dialog_manager.dialog_data["description"] = text
    await dialog_manager.next()


async def on_category_chosen(callback: CallbackQuery,
                             widget: Select,
                             dialog_manager: DialogManager,
                             item_id: str):
    dialog_manager.dialog_data["category_id"] = item_id
    await dialog_manager.next()


async def on_category_select_for_tasks(callback: CallbackQuery,
                                       widget: Select,
                                       dialog_manager: DialogManager,
                                       item_id: str):
    dialog_manager.dialog_data['selected_category'] = item_id
    await dialog_manager.switch_to(FSMTodoList.task_list_by_category)


async def on_create_category(message: Message,
                             widget: ManagedTextInput,
                             dialog_manager: DialogManager,
                             text: str):
    new_cat = await api_categories.create_category(text, message.from_user.id)
    dialog_manager.dialog_data["category_id"] = new_cat["id"]
    await dialog_manager.next()


async def on_create_category_from_categories(message: Message,
                                             widget: ManagedTextInput,
                                             dialog_manager: DialogManager,
                                             text: str):
    categories = await api_categories.get_categories(message.from_user.id)
    cat_names = [cat["name"] for cat in categories]
    if text not in cat_names:
        new_cat = await api_categories.create_category(text, message.from_user.id)

    await dialog_manager.switch_to(FSMTodoList.change_category)


async def on_date_selected(callback: CallbackQuery,
                           widget,
                           dialog_manager: DialogManager,
                           selected_date: date):
    dialog_manager.dialog_data["due_date"] = selected_date.isoformat()
    await dialog_manager.next()


# Переход к добавлению
async def on_add_task(callback: CallbackQuery,
                      button: Button,
                      dialog_manager: DialogManager):
    await dialog_manager.start(FSMTodoList.add_task, data=dialog_manager.start_data)


# Обработка ввода названия
async def save_title(message: Message,
                     widget: ManagedTextInput,
                     dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["title"] = text
    await dialog_manager.next()


async def on_confirm(callback: CallbackQuery,
                     button: Button,
                     dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    telegram_id = callback.from_user.id
    await api_tasks.create_task(
        telegram_id=str(telegram_id),
        title=data["title"],
        due_date=data.get("due_date"),
        due_time=data.get("due_time"),
        category_id=data.get("category_id"),
        description=data.get("description")
    )
    await dialog_manager.switch_to(FSMTodoList.my_tasks)
