import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
import httpx

from src.services.auth import AuthService
from src.storage.tokens import TokenStorage

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        token_storage = data['token_storage']
        auth_service = data['auth_service']
        user = event.from_user
        if not user:
            return
        data['current_user'] = user
        user_id = user.id
        token = await auth_service.get_auth_token(user_id, token_storage)
        if not token:
            return await event.answer("Authorization error. Please try again later.")

        return await handler(event, data)
