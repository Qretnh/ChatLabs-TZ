import datetime
import logging

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Back, Calendar, Select, CalendarConfig, SwitchTo, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput

from datetime import date

from FSM import TASKS

from services.api.tasks import get_tasks, create_task, delete_task
from services.api.categories import get_categories, create_category, delete_category

from environs import Env

from .getters import *
from .functions import *

env = Env()
env.read_env()

BASE_URL = env("API_BASE_URL")

DEFAULT_TIME = "18:00"

### ---------------- DIALOG -------------------


tasks_dialog = Dialog(
    Window(
        Const("Ваш персональный TO-DO лист\n\n"
              "<i>📖 Просмотреть все задачи</i> - \n"
              "Нажмите, чтобы просмотреть полный список задач\n\n"
              "<i>📋 Задачи по категориям</i> - \n"
              "Чтобы ➕ открыть задачи конкретной категории ИЛИ удалить/завершить✅ задачу\n\n"
              "<i>✏️ Изменить категории</i> - \n"
              "Удаление категорий\n\n"
              "<i>➕ Добавить задачу</i> - \n"
              "Создание новой задачи\n\n"
              "<i>📁 Архив</i> - \n"
              "Просмотреть завершенные задачи"),
        SwitchTo(Const("➕ Добавить задачу"),
                 id='add_task',
                 state=TASKS.add_task),
        SwitchTo(Const("📖 Просмотреть все задачи"),
                 id='open_tasks',
                 state=TASKS.my_tasks),
        SwitchTo(Const("📋 Управление задачами"),
                 id='tasks_by_category',
                 state=TASKS.tasks_by_category),
        SwitchTo(Const("✏️ Изменить категории"),
                 id='change_category',
                 state=TASKS.change_category),
        SwitchTo(Const("📁 Архив"),
                 id='archive',
                 state=TASKS.archive),
        state=TASKS.start
    ),

    # Вывод списка задач
    Window(
        Format("📝 <b>Актуальные задачи</b>:\n\n{tasks_text}\n"),
        Const("Чтобы добавить новую задачу — нажмите кнопку ниже 👇"),
        Button(Const("➕ Добавить задачу"),
               id="add_task",
               on_click=on_add_task),
        SwitchTo(Const("🔙 Назад"),
                 id='confirm_task_',
                 state=TASKS.start),
        state=TASKS.my_tasks,
        getter=getter_tasks_data
    ),

    # Ввод названия
    Window(
        Const("✍️ <b>Введите название новой задачи</b>:\n\n"
              "Например: \"Сходить в спортзал\" или \"Закончить отчёт\" 🗒"),
        TextInput(id='input_title',
                  type_factory=lambda text: text,
                  on_success=save_title),
        Back(Const("🔙 Назад")),
        state=TASKS.add_task
    ),

    # Выбор даты выполнения
    Window(
        Const("📅 Выберите дату выполнения задачи (Нажмите на подходящую дату в календаре):"),
        Calendar(id="calendar",
                 config=CalendarConfig(min_date=datetime.date.today()),
                 on_click=on_date_selected),
        Back(Const("🔙 Назад")),
        state=TASKS.pick_date
    ),

    # Выбор категории для создания
    Window(
        Const("🗂 Выберите категорию из списка, либо введите название новой категории (она создастся автоматически):"),
        Select(
            Format("{item[name]}"),
            items="categories",
            item_id_getter=lambda c: str(c["id"]),
            id="category_select",
            on_click=on_category_chosen
        ),
        TextInput(
            id="new_category_input",
            type_factory=lambda text: text,
            on_success=on_create_category
        ),
        Back(Const("🔙 Назад")),
        state=TASKS.pick_category,
        getter=getter_categories
    ),

    # Ввод описания задачи
    Window(
        Const("✍️ Введите описание задачи или нажмите кнопку 'Без описания', если оно не требуется"),
        TextInput(
            id='input_description',
            type_factory=lambda text: text,
            on_success=on_description_updated
        ),
        Button(Const("Без описания"),
               id="no_desc",
               on_click=on_no_description),
        Back(Const("🔙 Назад")),
        state=TASKS.input_description
    ),

    # Ввод времени выполнения задачи (Дефолт 18:00)
    Window(
        Const("⏰ Введите время выполнения задачи в формате HH:MM (пример - 09:30)\n\n"
              "Или нажмите 'Пропустить' — по умолчанию задача будет на 18:00"),
        TextInput(
            id='input_time',
            type_factory=lambda text: text,
            on_success=on_time_entered
        ),
        Button(Const("Пропустить"),
               id="skip_time",
               on_click=on_skip_time),
        Back(Const("🔙 Назад")),
        state=TASKS.input_time
    ),

    # Подтверждение выполнения таски
    Window(
        Format("✅ <b>Подтвердите добавление задачи</b>:\n\n"
               "🗂 <b>Задача:</b> {title}\n"
               "📅 <b>Выполнить до:</b> {due_date} {due_time}\n"
               "📝 <b>Описание:</b> {description}\n\n"
               "Если всё верно — жмите ✅"),
        Button(Format("✅ Подтвердить"),
               id="confirm",
               on_click=on_confirm),
        Back(Const("🔙 Назад")),
        getter=getter_confirm_task,
        state=TASKS.confirm_task
    ),

    # Выбор категории при просмотре задач по категориям
    Window(
        Const("📂 Выберите категорию для просмотра задач\n\n"
              "(Отображаются только категории, в которых есть задачи)"),
        ScrollingGroup(
            Select(
                Format("{item}"),
                items="grouped_tasks",
                item_id_getter=lambda item: item,
                id="category_choice",
                on_click=on_category_select_for_tasks
            ),
            id="categories_scroll",
            width=1,
            height=5
        ),
        SwitchTo(Const("🔙 Назад"),
                 id="back_from_manage_categories",
                 state=TASKS.start),
        getter=getter_tasks_by_category,
        state=TASKS.tasks_by_category
    ),

    # Окно задач в категории
    Window(
        Format("📂 <b>Задачи в категории {category}</b>\n\n"),
        ScrollingGroup(
            Select(
                Format("{item[title]}"),
                items="TODO",
                item_id_getter=lambda task: task['id'],
                id="task_in_category",
                on_click=view_task_detail
            ),
            id="task_scroll",
            width=1,
            height=5
        ),
        Back(Const("🔙 Назад")),
        getter=getter_selected_category_tasks,
        state=TASKS.task_list_by_category
    ),

    # Окно таски
    Window(
        Format("📌 <b>{task[title]}</b>\n\n"
               "Категория: <b>{task[category][name]}</b>\n\n"
               "Дата создания: <b>{created_at} </b>\n"
               "Дата исполнения: <b>{due_date} {task[due_time]}</b>\n"
               "Описание: {task[description]}"),
        Button(Const("✅ Завершить задачу"),
               id='complete',
               on_click=complete_task_handler),
        Button(Const("🗑 Удалить задачу"),
               id="delete_task",
               on_click=delete_task_handler),
        SwitchTo(Const("✍️ Обновить описание"),
                 id='update_description',
                 state=TASKS.update_task_description),
        Back(Const("🔙 Назад")),
        getter=getter_task,
        state=TASKS.task_detail
    ),

    # Окно категорий
    Window(
        Const("🗂 Управление категориями. \n\nНажмите на название категории, если хотите её удалить\n\n"
              "Для добавления новой - воспользуйтесь кнопкой ниже"),
        ScrollingGroup(
            Select(
                Format("❌ {item[name]}"),
                items="categories",
                item_id_getter=lambda cat: cat["id"],
                id="category_delete",
                on_click=delete_category_handler
            ),
            id="manage_scroll",
            width=1,
            height=5
        ),
        SwitchTo(Const("✍️ Добавить категорию"),
                 id="add_new_category",
                 state=TASKS.add_new_category),
        SwitchTo(Const("🔙 Назад"),
                 id="back_from_manage_categories",
                 state=TASKS.start),
        getter=getter_manage_categories,
        state=TASKS.change_category
    ),

    # Ввод названия новой категории
    Window(
        Const("Введите название новой категории"),
        TextInput(
            id="new_category_input",
            type_factory=lambda text: text,
            on_success=on_create_category_from_categories
        ),
        Back(Const("🔙 Назад")),
        state=TASKS.add_new_category
    ),

    # Ввод нового описания задачи
    Window(
        Const("Введите новое описание задачи"),
        TextInput(
            id='input_description',
            type_factory=lambda text: text,
            on_success=on_description_entered
        ),
        state=TASKS.update_task_description
    ),

    # Архив - выполненные таски
    Window(
        Const("Выполненные задачи"),
        ScrollingGroup(
            Select(
                Format("✅ {item[title]}"),
                items="tasks",
                item_id_getter=lambda task: task['id'],
                id="task_in_category",
                on_click=view_task_archive
            ),
            id="task_scroll",
            width=1,
            height=5
        ),
        SwitchTo(Const("🔙 Назад"),
                 id='back_from_archive',
                 state=TASKS.start),
        getter=getter_archive,
        state=TASKS.archive
    ),

    # Окно архивной таски
    Window(
        Format("📌 <b>{task[title]}</b>\n\n"
               "Категория: <b>{task[category][name]}</b>\n\n"
               "Дата создания: <b>{created_at} </b>\n"
               "Дата исполнения: <b>{due_date} {task[due_time]}</b>\n"
               "Описание: {task[description]}\n\n"
               "✅ Выполнено!"),
        Button(Const("🗑 Удалить задачу"),
               id="delete_task",
               on_click=delete_task_handler),
        Back(Const("🔙 Назад")),
        getter=getter_task,
        state=TASKS.archive_task_detail
    ),

)
