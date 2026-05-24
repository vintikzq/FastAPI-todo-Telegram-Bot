from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from src.keyboards.main_menu import get_main_menu_keyboard
from src.keyboards.task_menu import get_stats_buttons
from src.schemas.enums import MenuButtons
from src.services.tasks import TaskService

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message, current_user: User):
    await message.answer(
        f"Welcome, {current_user.first_name}! I'm your task assistant. Use the menu below to manage your goals.",
        reply_markup=get_main_menu_keyboard(),
    )


@router.message(F.text == MenuButtons.STATS)
async def stats_handler(
    message: Message, task_service: TaskService, current_user: User, bot: Bot, state: FSMContext
):
    data = await state.get_data()
    msg_id = data.get("last_msg_id")

    try:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id, message_id=msg_id, reply_markup=None
        )
    except TelegramBadRequest:
        pass

    data = await task_service.get_stats_counter(current_user.id)

    sent_msg = await message.answer(
        text=data.format_to_pretty_stats(), parse_mode="HTML", reply_markup=get_stats_buttons()
    )

    if isinstance(sent_msg, Message):
        await state.update_data(last_msg_id=sent_msg.message_id)
