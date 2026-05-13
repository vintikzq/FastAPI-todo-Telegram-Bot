import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        auth_service = data['auth_service']
        user = event.from_user

        if not user:
            return

        data['current_user'] = user
        user_id = user.id
        token = await auth_service.get_auth_token(user_id)

        if not token:
            error_text = "Authorization error. Please try again later."
            if isinstance(event, CallbackQuery):
                return await event.answer(error_text, show_alert=True)
            return await event.answer(error_text)

        return await handler(event, data)
