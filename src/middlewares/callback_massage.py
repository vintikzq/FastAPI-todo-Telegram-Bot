from collections.abc import Awaitable, Callable
from typing import Any, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message


class CallBackMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any]
    ) -> Any:

        if event.message and isinstance(event.message, Message):
            data['callback_msg'] = event.message

        return await handler(event, data)
