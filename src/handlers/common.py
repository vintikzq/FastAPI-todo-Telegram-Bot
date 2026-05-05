from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.keyboards.auth_menu import get_auth_keyboard


router = Router()


@router.message(Command('start'))
async def start_handler(message: Message):
    await message.answer("Hello there! Choose action:", reply_markup=await get_auth_keyboard())
