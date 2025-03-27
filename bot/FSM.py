from aiogram.fsm.state import StatesGroup, State


class FSMTodoList(StatesGroup):
    start = State()

    my_tasks = State()
    add_task = State()
    confirm_task = State()
    task_detail = State()

    task_list_by_category = State()
    tasks_by_category = State()
    add_new_category = State()
    change_category = State()

    pick_date = State()
    pick_category = State()
    input_description = State()
    input_time = State()
    update_task_description = State()

    archive = State()
    archive_task_detail = State()
