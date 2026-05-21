from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from aiogram_calendar import SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct
import pytest

from src.handlers.task_edit import change_task_deadline, change_task_description, change_task_name, change_task_priority, process_new_deadline, process_new_task_description, process_new_task_name, process_new_task_priority, process_update_menu
from src.schemas.callbacks import TaskPriorityCallback, TaskUpdateCallback, TaskViewCallback
from src.schemas.enums import ActionsUpdate, ActionsView,  TodoPriority
from src.states.tasks import UpdateTaskState


@pytest.mark.asyncio
async def test_process_update_menu_should_ask_for_update_fields_and_show_keyboard(
    callback_query, message
):
    callback_data = TaskViewCallback(
        action=ActionsView.UPDATE, page=1, task_id=1)

    await process_update_menu(callback_query, callback_data, message)

    message_kwargs = message.edit_text.call_args.kwargs

    message.edit_text.assert_called_once()
    assert "Select fields" in message_kwargs['text']
    assert message_kwargs['reply_markup'] is not None
    callback_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_change_task_name_should_ask_for_name_and_set_state(
    callback_query, message, state
):
    callback_data = TaskUpdateCallback(
        to_update=ActionsUpdate.NAME, task_id=1, page=1)

    await change_task_name(callback_query, callback_data, message, state)

    message_kwargs = message.edit_text.call_args.kwargs

    assert "new task name" in message_kwargs['text']
    assert message_kwargs['reply_markup'] is None
    callback_query.answer.assert_called_once()
    assert (await state.get_state()) == UpdateTaskState.waiting_for_new_task_name


@pytest.mark.asyncio
async def test_process_new_task_name_should_update_task_name_and_clear_state(
    message, task_service,
    current_user, bot, prepared_update_state
):
    message.text = 'job'

    await process_new_task_name(message, task_service, current_user, bot, prepared_update_state)

    message.delete.assert_called_once()

    task_update_kwargs = task_service.update_task_by_id.call_args.kwargs
    assert task_update_kwargs['user_id'] == current_user.id
    assert task_update_kwargs['task_id'] == 1
    assert task_update_kwargs['data'].name == message.text
    assert (await prepared_update_state.get_state()) == None


@pytest.mark.asyncio
async def test_change_task_description_should_ask_for_description_and_set_state(
    callback_query, message, state
):
    callback_data = TaskUpdateCallback(
        to_update=ActionsUpdate.DESCRIPTION, task_id=1, page=1)

    await change_task_description(callback_query, callback_data, message, state)

    message_kwargs = message.edit_text.call_args.kwargs

    assert "new task description" in message_kwargs['text']
    assert message_kwargs['reply_markup'] is None
    callback_query.answer.assert_called_once()
    assert (await state.get_state()) == UpdateTaskState.waiting_for_new_description


@pytest.mark.asyncio
async def test_process_new_task_description_should_update_description_and_clear_state(
    message, task_service,
    current_user, bot, prepared_update_state
):
    message.text = 'today'

    await process_new_task_description(message, task_service, current_user, bot, prepared_update_state)

    message.delete.assert_called_once()

    task_update_kwargs = task_service.update_task_by_id.call_args.kwargs
    assert task_update_kwargs['user_id'] == current_user.id
    assert task_update_kwargs['task_id'] == 1
    assert task_update_kwargs['data'].description == message.text
    assert (await prepared_update_state.get_state()) == None


@pytest.mark.asyncio
async def test_change_task_priority_should_ask_for_priority_set_keyboard_and_set_state(
    callback_query, message, state
):
    callback_data = TaskUpdateCallback(
        to_update=ActionsUpdate.PRIORITY, task_id=1, page=1)

    await change_task_priority(callback_query, callback_data, message, state)

    message_kwargs = message.edit_text.call_args.kwargs

    assert "new task priority" in message_kwargs['text']
    assert message_kwargs['reply_markup'] is not None
    callback_query.answer.assert_called_once()
    assert (await state.get_state()) == UpdateTaskState.waiting_for_new_task_priority


@pytest.mark.asyncio
async def test_process_new_task_priority_should_update_priority_and_clear_state(
    callback_query, message, task_service,
    current_user, bot, prepared_update_state
):
    callback_data = TaskPriorityCallback(value=TodoPriority.HIGH)

    await process_new_task_priority(
        callback_query, callback_data,
        message, task_service, current_user,
        bot, prepared_update_state
    )

    task_update_kwargs = task_service.update_task_by_id.call_args.kwargs
    assert task_update_kwargs['user_id'] == current_user.id
    assert task_update_kwargs['task_id'] == 1
    assert task_update_kwargs['data'].priority == callback_data.value
    assert (await prepared_update_state.get_state()) == None


@pytest.mark.asyncio
async def test_change_task_deadline_should_ask_for_deadline_set_keyboard_and_set_state(
    callback_query, message, state
):
    callback_data = TaskUpdateCallback(
        to_update=ActionsUpdate.DEADLINE, task_id=1, page=1)

    await change_task_deadline(callback_query, callback_data, message, state)

    message_kwargs = message.edit_text.call_args.kwargs

    assert "new task deadline" in message_kwargs['text']
    assert message_kwargs['reply_markup'] is not None
    callback_query.answer.assert_called_once()
    assert (await state.get_state()) == UpdateTaskState.waiting_for_new_deadline_date


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "calendar_return, act_value, expected_state, should_update_task",
    [
        pytest.param((True,  datetime.now() - timedelta(days=1)),
                     SimpleCalAct.day, UpdateTaskState.waiting_for_new_deadline_date,
                     False, id="yesterday_date_should_ask_date_again"),
        pytest.param((True,  datetime.now() + timedelta(days=1)),
                     SimpleCalAct.day, None, True,
                     id="tomorrow_date_should_successfully_process_task_update"),
        pytest.param((False, None),
                     SimpleCalAct.cancel, None, True,
                     id="cancel_button_selected_should_successfully_process_task_update_without_deadline")
    ]
)
async def test_process_new_deadline_should_process_correct_based_on_selected_data(
    callback_query, message,
    prepared_update_state, task_service, current_user,
    calendar_return, expected_state,
    should_update_task, act_value, bot
):
    await prepared_update_state.set_state(UpdateTaskState.waiting_for_new_deadline_date)
    await prepared_update_state.update_data(name='Task', priority=TodoPriority.HIGH, description=None)
    callback_data = SimpleCalendarCallback(act=act_value)

    with patch("src.handlers.task_edit.SimpleCalendar.process_selection", new_callable=AsyncMock) as mock_selection:
        mock_selection.return_value = calendar_return
        await process_new_deadline(
            callback_query, callback_data, message,
            task_service, current_user, bot,
            prepared_update_state
        )

    assert await prepared_update_state.get_state() == expected_state
    assert should_update_task == task_service.update_task_by_id.called
