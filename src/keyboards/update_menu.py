from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.schemas.callbacks import TaskPaginatorCallBack, TaskUpdateCallback
from src.schemas.enums import ActionsNav, ActionsUpdate


def get_update_buttons(task_id: int, page: int, is_archive: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    buttons = []
    for btn in ActionsUpdate:
        buttons.append(
            InlineKeyboardButton(
                text=btn.label,
                callback_data=TaskUpdateCallback(
                    to_update=btn, task_id=task_id, page=page, is_archive=is_archive
                ).pack(),
            )
        )

    buttons.append(
        InlineKeyboardButton(
            text="🔙 Back to task",
            callback_data=TaskPaginatorCallBack(
                action=ActionsNav.VIEW, page=page, task_id=task_id, is_archive=is_archive
            ).pack(),
        )
    )
    builder.row(*buttons)

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)
