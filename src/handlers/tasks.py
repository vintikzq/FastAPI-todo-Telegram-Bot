import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import httpx

from src.services.tasks import TaskService


router = Router()

logger = logging.getLogger(__name__)


@router.message(Command('tasks'))
async def get_all_tasks(message: Message, task_service: TaskService):
    try:
        user_id = message.from_user.id if message.from_user else None
        if user_id is not None:
            res = await task_service.get_tasks(user_id)
            await message.answer(f"{len(res)}")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            await message.answer("Need authorize first.\nUse /login.")
        else:
            logger.error(
                f"Connection Error {e.response.status_code} - {e.response.text}")
