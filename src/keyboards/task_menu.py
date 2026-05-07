from aiogram.filters import callback_data
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from src.schemas.callbacks import TaskFormCallBack, TaskPriorityCallback
from src.schemas.enums import TodoPriority, TodoStatus


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
