from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.schemas.enums import MenuButtons


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=MenuButtons.MY_TASKS))
    builder.add(KeyboardButton(text=MenuButtons.CREATE_TASK))
    builder.add(KeyboardButton(text=MenuButtons.STATS))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Choose action...")
