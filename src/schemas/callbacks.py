from aiogram.filters.callback_data import CallbackData

from src.schemas.enums import ActionsNav, ActionsUpdate, ActionsView, TodoPriority, TodoStatus


class TaskPriorityCallback(CallbackData, prefix='prio'):
    value: TodoPriority


class TaskFormCallBack(CallbackData, prefix='task_form'):
    action: str


class TaskPaginatorCallBack(CallbackData, prefix='task_page'):
    action: ActionsNav
    page: int
    task_id: int | None = None
    is_archive: bool = False


class TaskViewCallback(CallbackData, prefix='task_view'):
    action:  ActionsView
    page: int
    task_id: int
    is_archive: bool = False


class TaskUpdateCallback(CallbackData, prefix='upd'):
    to_update: ActionsUpdate
    task_id: int
    page: int
    is_archive: bool = False


class TaskStatusCallback(CallbackData, prefix='stat'):
    new_status: TodoStatus
    task_id: int
    page: int
    is_archive: bool = False
