from aiogram import types


async def get_auth_keyboard():
    kb = [
        [types.KeyboardButton(text="Registration")],
        [types.KeyboardButton(text="Login")],
    ]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
