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
            if res:
                messages = []
                for data in res:
                    date = data.friendly_date
                    priority = data.emoji_priority
                    status = data.emoji_status
                    description = data.not_none_description
                    messages.append(
                        f"{priority} <b>{data.name}</b> {date} {status}\n<i>{description}</i>")
                await message.answer("\n".join(messages), parse_mode='HTML')
            if not res:
                await message.answer("Your tasks list is empty now!")
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            await message.answer("Need authorize first.\nUse /login.")
        else:
            logger.error(
                f"Connection Error {e.response.status_code} - {e.response.text}")
