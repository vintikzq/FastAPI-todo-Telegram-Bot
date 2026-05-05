import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import httpx

from src.services.auth import AuthService
from src.states.auth import AuthStates
from src.storage.tokens import TokenStorage


router = Router()

logger = logging.getLogger(__name__)


@router.message(Command('login'))
async def login_user(message: Message, state: FSMContext):
    await message.answer("Enter your login")
    await state.set_state(AuthStates.waiting_for_login)


@router.message(AuthStates.waiting_for_login)
async def get_login_and_password_by_user(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Enter your password")
    await state.set_state(AuthStates.waiting_for_password)


@router.message(AuthStates.waiting_for_password)
async def process_login_user(message: Message, state: FSMContext, auth_service: AuthService, token_storage: TokenStorage):
    try:
        await state.update_data(password=message.text)
        user_data = await state.get_data()
        response = await auth_service.login_user(login=user_data['login'], password=user_data['password'])
        token = response.get("access_token")
        user_id = message.from_user.id if message.from_user else None
        await message.delete()
        if user_id is not None:
            await token_storage.save_token(user_id, token)
            await message.answer("Login is successful")
        else:
            await message.answer("Cannot log your access token")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            await message.answer(f"{e.response.json().get('detail', 'Login error')}")
        else:
            logger.error(
                f"Login Failed: {e.response.status_code} - {e.response.text}")
            await message.answer("Something went wrong in server")
    await state.clear()
