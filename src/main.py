import asyncio
import logging

from aiogram import Bot, Dispatcher
import httpx
from src.handlers.common import router as common_handler_router
from src.handlers.tasks import router as tasks_handler_router
from src.handlers.task_create import router as create_tasks_handler_router
from src.handlers.task_edit import router as update_tasks_hendler_router
from src.core.config import settings
from src.middlewares.auth import AuthMiddleware
from src.middlewares.callback_massage import CallBackMessageMiddleware
from src.services.auth import AuthService
from src.services.tasks import TaskService
from src.storage.tokens import TokenStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.callback_query.middleware(CallBackMessageMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.include_router(common_handler_router)
    dp.include_router(tasks_handler_router)
    dp.include_router(create_tasks_handler_router)
    dp.include_router(update_tasks_hendler_router)
    token_storage = TokenStorage()
    async with httpx.AsyncClient() as session:
        task_service = TaskService(session, token_storage)
        auth_service = AuthService(session, token_storage)

        await dp.start_polling(bot, task_service=task_service, auth_service=auth_service, token_storage=token_storage)

if __name__ == '__main__':
    asyncio.run(main())
