from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.schemas.callbacks import TaskFormCallBack, TaskPaginatorCallBack, TaskPriorityCallback, TaskStatusCallback, TaskViewCallback
from src.schemas.enums import ActionsNav, ActionsView, TodoPriority, TodoStatus
from src.schemas.tasks import TaskResponse


def get_task_priority_buttons():
    builder = InlineKeyboardBuilder()
    for priority in TodoPriority:
        builder.add(InlineKeyboardButton(
            text=priority.label,
            callback_data=TaskPriorityCallback(value=priority).pack()
        ))
    return builder.as_markup(resize_keyboard=True)


def skip_button():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Skip',
        callback_data=TaskFormCallBack(action='skip').pack()))

    return builder.as_markup(resize_keyboard=True)


def get_navigation_buttons(tasks: list[TaskResponse], current_page: int, has_next: bool, is_archive: bool = False):
    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.row(InlineKeyboardButton(
            text=task.friendly_format_for_buttons(),
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.VIEW,
                page=current_page,
                task_id=task.id,
                is_archive=is_archive
            ).pack()
        ))

    buttons = []

    if current_page > 1:
        buttons.append(InlineKeyboardButton(
            text='⬅️',
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.PAGE_DOWN, page=current_page - 1, is_archive=is_archive).pack()
        ))

    buttons.append(InlineKeyboardButton(
        text=f'• {current_page} •',
        callback_data='ignore'
    ))

    if has_next:
        buttons.append(InlineKeyboardButton(
            text='➡️',
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.PAGE_UP, page=current_page + 1, is_archive=is_archive).pack()
        ))

    builder.row(*buttons)

    return builder.as_markup(resize_keyboard=True)


def get_task_buttons(task_id: int, current_page: int, status: TodoStatus | None = None, is_archive: bool = False):
    builder = InlineKeyboardBuilder()
    if status is not None:
        status_btns = []
        for s in TodoStatus:
            if s == status or s == TodoStatus.ACTIVE:
                continue
            status_btns.append(
                InlineKeyboardButton(
                    text=s.label,
                    callback_data=TaskStatusCallback(
                        new_status=s,
                        task_id=task_id,
                        page=current_page,
                        is_archive=is_archive
                    ).pack()
                )
            )
        builder.row(*status_btns)

    delete_btn = InlineKeyboardButton(
        text='Delete 🗑️',
        callback_data=TaskViewCallback(
            action=ActionsView.DELETE,
            task_id=task_id,
            page=current_page,
            is_archive=is_archive).pack()
    )

    update_btn = InlineKeyboardButton(
        text='Update ⚙️',
        callback_data=TaskViewCallback(
            action=ActionsView.UPDATE,
            task_id=task_id,
            page=current_page,
            is_archive=is_archive).pack()
    )

    if is_archive:
        back_to_list_btn = InlineKeyboardButton(
            text="🔙 Back to archive",
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.LIST,
                page=current_page,
                is_archive=True).pack()
        )
    else:

        back_to_list_btn = InlineKeyboardButton(
            text="🔙 Back to list",
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.LIST,
                page=current_page).pack()
        )

    builder.row(delete_btn, update_btn)
    builder.row(back_to_list_btn)

    return builder.as_markup(resize_keyboard=True)


def get_stats_buttons():
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text='Open archive 🗄️',
        callback_data=TaskPaginatorCallBack(
            action=ActionsNav.ARCHIVE,
            page=1, is_archive=True
        ).pack()))
    return builder.as_markup(resize_keyboard=True)
