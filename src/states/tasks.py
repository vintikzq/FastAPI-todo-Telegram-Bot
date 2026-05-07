from aiogram.fsm.state import State, StatesGroup


class CreateTaskState(StatesGroup):
    waiting_for_task_name = State()
    waiting_for_task_priority = State()
    waiting_for_deadline_date = State()
    waiting_for_description = State()
