from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, User

from src.keyboards.main_menu import get_main_menu_keyboard


router = Router()


@router.message(Command('start'))
async def start_handler(message: Message, current_user: User):
    await message.answer(f"Welcome, {current_user.first_name}! I'm your task assistant. Use the menu below to manage your goals.", reply_markup=get_main_menu_keyboard())
