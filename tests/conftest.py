from unittest.mock import AsyncMock, MagicMock

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message, User
import pytest

from src.schemas.tasks import TaskResponse
from src.services.tasks import TaskService


@pytest.fixture()
async def state():
    storage = MemoryStorage()
    key = StorageKey(
        bot_id=1, chat_id=1, user_id=1
    )
    fsm_context = FSMContext(storage=storage, key=key)

    yield fsm_context

    await storage.close()


@pytest.fixture()
def bot():
    mock_bot = MagicMock(spec=Bot)

    mock_bot.edit_message_reply_markup = AsyncMock(return_value=None)
    mock_bot.edit_message_text = AsyncMock(return_value=None)

    return mock_bot


@pytest.fixture()
def task_service():
    mock_task_service = MagicMock(spec=TaskService)

    mock_task_service.get_stats_counter = AsyncMock()
    mock_task_service.create_task = AsyncMock()

    mock_task_service.get_tasks = AsyncMock()

    return mock_task_service


@pytest.fixture()
def current_user():
    mock_current_user = MagicMock(spec=User)

    mock_current_user.id = 999

    return mock_current_user


@pytest.fixture()
def message():
    mock_message = MagicMock(spec=Message)

    mock_chat = MagicMock()
    mock_chat.id = 999
    mock_message.chat = mock_chat
    mock_message.delete = AsyncMock(return_value=None)
    mock_message.answer = AsyncMock(return_value=None)
    mock_message.edit_text = AsyncMock(return_value=None)

    return mock_message


@pytest.fixture()
def fake_stats_response():
    mock_response = MagicMock()

    mock_response.format_to_pretty_stats.return_value = "<b>Your statistics:</b>\n\nTotal tasks: 999\nDone tasks: 222\nTasks at work: 777"

    return mock_response


@pytest.fixture()
def callback_query():
    mock_callback_query = MagicMock(spec=CallbackQuery)
    mock_callback_query.answer = AsyncMock(return_value=None)

    return mock_callback_query


@pytest.fixture()
def fake_task():
    mock_fake_task = MagicMock(spec=TaskResponse)
    mock_fake_task.id = 1
    mock_fake_task.friendly_format_for_buttons = MagicMock(
        return_value='Task')
    return mock_fake_task
