from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, User

from src.keyboards.update_menu import get_update_buttons
from src.schemas.callbacks import TaskViewCallback
from src.schemas.enums import ActionsView
from src.services.tasks import TaskService


router = Router()


@router.callback_query(TaskViewCallback.filter(F.action == ActionsView.UPDATE))
async def process_update_menu(
    callback: CallbackQuery,
    callback_data: TaskViewCallback,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message
):

    await callback_msg.edit_text(text="Select fields to edit:", reply_markup=get_update_buttons(
        task_id=callback_data.task_id, page=callback_data.page))
