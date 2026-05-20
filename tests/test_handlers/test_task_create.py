from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from aiogram_calendar import SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct
import pytest

from src.handlers.task_create import process_deadline, process_task_description, process_task_description_skip, process_task_name, process_task_priority, start_task_creation
from src.schemas.callbacks import TaskPriorityCallback
from src.schemas.enums import MenuButtons, TodoPriority
from src.states.tasks import CreateTaskState


@pytest.mark.asyncio
async def test_start_task_creation_should_ask_task_name_and_set_state(
    message, state
):
    message.text = MenuButtons.CREATE_TASK
    message.answer.return_value = MagicMock(message_id=42)
    await start_task_creation(message, state)

    data = await state.get_data()
    current_state = await state.get_state()

    assert message.answer.call_count == 2
    assert data['msg_id'] == 42
    assert current_state == CreateTaskState.waiting_for_task_name


@pytest.mark.asyncio
async def test_process_task_name_should_save_task_name_ask_for_description_and_set_state(
    message, state, bot
):
    message.text = "Some task"
    await state.set_state(CreateTaskState.waiting_for_task_name)
    await state.update_data(msg_id=42)

    await process_task_name(message, state, bot)

    data = await state.get_data()
    current_state = await state.get_state()

    msg_kwargs = bot.edit_message_text.call_args.kwargs
    message.delete.assert_called_once()
    assert data['name'] == "Some task"
    assert "Name saved" in msg_kwargs['text']
    assert msg_kwargs['reply_markup'] is not None
    assert msg_kwargs['message_id'] == 42
    assert current_state == CreateTaskState.waiting_for_description


@pytest.mark.asyncio
async def test_process_task_description_skip_should_save_none_as_description_ask_for_priority_and_set_state(
    callback_query, state, message
):
    await state.set_state(CreateTaskState.waiting_for_description)

    await process_task_description_skip(callback_query, state, message)

    data = await state.get_data()
    msg_kwargs = message.edit_text.call_args.kwargs

    callback_query.answer.assert_called_once_with('Skipped')
    assert data['description'] is None
    assert msg_kwargs['reply_markup'] is not None
    assert await state.get_state() == CreateTaskState.waiting_for_task_priority


@pytest.mark.asyncio
async def test_process_task_description_should_save_description_ask_for_priority_and_set_state(
    bot, state, message
):
    await state.set_state(CreateTaskState.waiting_for_description)
    message.text = "Some task description"
    await state.update_data(msg_id=42)

    await process_task_description(message, state, bot)

    data = await state.get_data()
    msg_kwargs = bot.edit_message_text.call_args.kwargs

    bot.edit_message_text.assert_called_once()
    message.delete.assert_called_once()
    assert data['description'] is not None
    assert "Now select priority" in msg_kwargs['text']
    assert msg_kwargs['reply_markup'] is not None
    assert await state.get_state() == CreateTaskState.waiting_for_task_priority


@pytest.mark.asyncio
async def test_process_task_priority_should_save_priority_and_set_state(
    callback_query, message, state
):
    callback_data = TaskPriorityCallback(value=TodoPriority.HIGH)
    await state.set_state(CreateTaskState.waiting_for_task_priority)

    await process_task_priority(callback_query, message, callback_data, state)

    callback_query.answer.assert_called_once()

    assert message.edit_text.call_args.kwargs['reply_markup'] is not None
    assert (await state.get_data())['priority'] == TodoPriority.HIGH
    assert await state.get_state() == CreateTaskState.waiting_for_deadline_date


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "calendar_return, act_value, expected_state, should_create_task",
    [
        pytest.param((True,  datetime.now() - timedelta(days=1)),
                     SimpleCalAct.day, CreateTaskState.waiting_for_deadline_date,
                     False, id="yesterday_date_should_ask_date_again"),
        pytest.param((True,  datetime.now() + timedelta(days=1)),
                     SimpleCalAct.day, None, True,
                     id="tomorrow_date_should_successfully_process_task_creation"),
        pytest.param((False, None),
                     SimpleCalAct.cancel, None, True,
                     id="cancel_button_selected_should_successfully_process_task_creation_without_deadline")
    ]
)
async def test_process_deadline_should_process_correct_based_on_selected_data(
    callback_query, message,
    state, task_service, current_user,
    calendar_return, expected_state,
    should_create_task, act_value
):
    await state.set_state(CreateTaskState.waiting_for_deadline_date)
    await state.update_data(name='Task', priority=TodoPriority.HIGH, description=None)
    callback_data = SimpleCalendarCallback(act=act_value)

    with patch("src.handlers.task_create.SimpleCalendar.process_selection", new_callable=AsyncMock) as mock_selection:
        mock_selection.return_value = calendar_return
        await process_deadline(
            callback_query, message,
            callback_data, state, task_service,
            current_user
        )

    assert await state.get_state() == expected_state
    assert should_create_task == task_service.create_task.called
