from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class CallBackMessageMiddleware(BaseMiddleware):
    """
    CallbackQuery updates interceptor.

    Extracts the underlying Message object and injects it into the handler data context.
    """

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any],
    ) -> Any:

        if event.message and isinstance(event.message, Message):
            data["callback_msg"] = event.message

        return await handler(event, data)
