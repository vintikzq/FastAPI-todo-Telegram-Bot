from aiogram.filters.callback_data import CallbackData

from src.schemas.enums import ActionsNav, ActionsUpdate, ActionsView, TodoStatus


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
    page: int
    task_id: int


class TaskUpdateCallback(CallbackData, prefix='upd'):
    to_update: ActionsUpdate
    task_id: int
    page: int


class TaskStatusCallback(CallbackData, prefix='stat'):
    new_status: TodoStatus
    task_id: int
    page: int
