import asyncio

from aiogram import Bot, Dispatcher
import httpx
from src.handlers.common import router as common_handler_router
from src.core.config import settings
from src.services.tasks import TaskService


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common_handler_router)
    async with httpx.AsyncClient() as session:
        task_service = TaskService(session)
        await dp.start_polling(bot, task_service=task_service)

if __name__ == '__main__':
    asyncio.run(main())
