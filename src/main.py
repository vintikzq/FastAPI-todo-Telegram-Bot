import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher
from redis.asyncio import Redis

from src.core.config import settings
from src.handlers.archive_tasks import router as archive_tasks_router
from src.handlers.common import router as common_handler_router
from src.handlers.errors import errors_router as error_catch_router
from src.handlers.task_create import router as create_tasks_handler_router
from src.handlers.task_edit import router as update_tasks_handler_router
from src.handlers.tasks import router as tasks_handler_router
from src.middlewares.auth import AuthMiddleware
from src.middlewares.callback_massage import CallBackMessageMiddleware
from src.services.auth import AuthService
from src.services.tasks import TaskService
from src.storage.tokens import TokenStorage

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def on_startup(dispatcher: Dispatcher) -> None:
    session = httpx.AsyncClient()
    redis_client = Redis.from_url(url=settings.REDIS_URL, decode_responses=True)

    token_storage = TokenStorage(redis_client=redis_client)
    task_service = TaskService(session, token_storage)
    auth_service = AuthService(session, token_storage)

    dispatcher["redis_client"] = redis_client
    dispatcher["http_session"] = session
    dispatcher["token_storage"] = token_storage
    dispatcher["task_service"] = task_service
    dispatcher["auth_service"] = auth_service


async def on_shutdown(dispatcher: Dispatcher) -> None:
    session: httpx.AsyncClient = dispatcher["http_session"]
    redis_client: Redis = dispatcher["redis_client"]
    await session.aclose()
    await redis_client.close()


async def main():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.callback_query.middleware(CallBackMessageMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    dp.include_router(error_catch_router)
    dp.include_router(archive_tasks_router)
    dp.include_router(common_handler_router)
    dp.include_router(tasks_handler_router)
    dp.include_router(create_tasks_handler_router)
    dp.include_router(update_tasks_handler_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
