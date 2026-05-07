from aiogram.filters.callback_data import CallbackData

from src.schemas.enums import ActionsNav, ActionsView


class TaskPriorityCallback(CallbackData, prefix='prio'):
    value: str


class TaskFormCallBack(CallbackData, prefix='task_form'):
    action: str


class TaskPaginatorCallBack(CallbackData, prefix='task_page'):
    action: ActionsNav
    page: int
    task_id: int | None = None


class TaskViewCallback(CallbackData, prefix='task_view'):
    action:  ActionsView
    page: int | None = None
    task_id: int
