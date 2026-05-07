from aiogram.filters.callback_data import CallbackData


class TaskPriorityCallback(CallbackData, prefix='prio'):
    value: str


class TaskFormCallBack(CallbackData, prefix='task_form'):
    action: str
