from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.schemas.callbacks import TaskFormCallBack, TaskPaginatorCallBack, TaskPriorityCallback, TaskViewCallback
from src.schemas.enums import ActionsNav, ActionsView, TodoPriority, TodoStatus
from src.schemas.tasks import TaskResponse


def create_task_priority_buttons():
    builder = InlineKeyboardBuilder()
    for priority in [TodoPriority.LOW, TodoPriority.MEDIUM, TodoPriority.HIGH]:
        builder.add(InlineKeyboardButton(
            text=priority,
            callback_data=TaskPriorityCallback(value=priority.lower()).pack()
        ))
    return builder.as_markup(resize_keyboard=True)


def status_buttons():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=TodoStatus.PENDING, callback_data='status_pending'))
    builder.add(InlineKeyboardButton(
        text=TodoStatus.IN_PROGRESS, callback_data='status_progress'))
    builder.add(InlineKeyboardButton(
        text=TodoStatus.DONE, callback_data='status_done'))
    return builder.as_markup(resize_keyboard=True)


def skip_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Skip',
        callback_data=TaskFormCallBack(action='skip').pack()))

    return builder.as_markup(resize_keyboard=True)


def get_navigation_buttons(tasks: list[TaskResponse], current_page: int, has_next: bool):
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.row(InlineKeyboardButton(
            text=task.friendly_format_for_buttons(),
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.VIEW,
                page=current_page,
                task_id=task.id
            ).pack()
        ))

    buttons = []

    if current_page > 1:
        buttons.append(InlineKeyboardButton(
            text='⬅️',
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.PAGE_DOWN, page=current_page - 1).pack()
        ))

    buttons.append(InlineKeyboardButton(
        text=f'• {current_page} •',
        callback_data='ignore'
    ))

    if has_next:
        buttons.append(InlineKeyboardButton(
            text='➡️',
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.PAGE_UP, page=current_page + 1).pack()
        ))

    builder.row(*buttons)

    return builder.as_markup(resize_keyboard=True)


def get_task_buttons(task_id: int, current_page: int):
    builder = InlineKeyboardBuilder()

    delete_btn = (InlineKeyboardButton(
        text='Delete 🗑️',
        callback_data=TaskViewCallback(
            action=ActionsView.DELETE,
            task_id=task_id).pack()
    ))

    update_btn = (InlineKeyboardButton(
        text='Update ⚙️',
        callback_data=TaskViewCallback(
            action=ActionsView.UPDATE,
            task_id=task_id).pack()
    ))

    back_btn = (InlineKeyboardButton(
        text="🔙 Back to list",
        callback_data=TaskPaginatorCallBack(
            action=ActionsNav.LIST,
            page=current_page).pack()
    ))

    builder.row(delete_btn, update_btn)
    builder.row(back_btn)

    return builder.as_markup(resize_keyboard=True)
