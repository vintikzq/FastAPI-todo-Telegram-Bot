import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent

from src.core.exceptions import BackendServerError, NetworkConnectionError, NotAuthorizedError, ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)
errors_router = Router()

ERROR_MESSAGES = {
    ResourceNotFoundError: {'text': "Task not found", 'clear_state': True},
    BackendServerError: {'text': "Something went wrong on our end. Please try later.", 'clear_state': False},
    ValidationError: {'text': "Data is invalid.", 'clear_state': False},
    NotAuthorizedError: {'text': "You have not authorized.", 'clear_state': True},
    NetworkConnectionError: {'text': "Check your connection and try again.", 'clear_state': False},
}


@errors_router.errors()
async def errors_catch(event: ErrorEvent, state: FSMContext):
    """
    Global runtime exception dispatcher.

    Maps domain network errors into UI alerts, logs session context, and manages FSM stability.
    """

    exception_type = type(event.exception)
    error_info = ERROR_MESSAGES.get(
        exception_type, {'text': "Unknown error was detected", 'clear_state': False})

    message_text = error_info['text']

    callback = event.update.callback_query
    message = event.update.message

    chat_id = callback.message.chat.id if callback and callback.message else (
        message.chat.id if message else 'Unknown')

    user_id = callback.from_user.id if callback else (
        message.from_user.id if message and message.from_user else 'Unknown')

    logger.error(
        f"""Error :{event.exception}, Errortype: {exception_type},
        chat_id: {chat_id},
        user_id : {user_id}""", exc_info=True)

    if callback and callback.message is not None:
        await callback.message.answer(text=message_text)
    elif message:
        await message.answer(text=message_text)

    if error_info.get('clear_state'):
        await state.clear()
