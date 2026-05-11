from aiogram.fsm.state import State, StatesGroup


class CreateTaskState(StatesGroup):
    waiting_for_task_name = State()
    waiting_for_task_priority = State()
    waiting_for_deadline_date = State()
    waiting_for_description = State()


class UpdateTaskState(StatesGroup):
    waiting_for_new_task_name = State()
    waiting_for_new_task_priority = State()
    waiting_for_new_deadline_date = State()
    waiting_for_new_description = State()
