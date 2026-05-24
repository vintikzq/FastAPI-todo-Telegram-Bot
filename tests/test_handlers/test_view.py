import pytest

from src.handlers.archive_tasks import pagination_archive_tasks
from src.handlers.common import stats_handler
from src.handlers.tasks import pagination_tasks, process_delete_task, update_status
from src.schemas.callbacks import TaskPaginatorCallBack, TaskStatusCallback, TaskViewCallback
from src.schemas.enums import ActionsNav, ActionsView, MenuButtons, TodoStatus


@pytest.mark.asyncio
async def test_stats_handler_should_delete_previous_keyboard_and_write_user_stats(
    state, bot, mock_task_service, message, fake_stats_response, current_user
):
    await state.update_data(last_msg_id=111)
    message.text = MenuButtons.STATS
    mock_task_service.get_stats_counter.return_value = fake_stats_response

    await stats_handler(message, mock_task_service, current_user, bot, state)

    assert message.answer.call_args.kwargs["reply_markup"] is not None

    assert "Tasks at work" in message.answer.call_args.kwargs["text"]
    bot.edit_message_reply_markup.assert_called_once_with(
        chat_id=message.chat.id, message_id=111, reply_markup=None
    )

    mock_task_service.get_stats_counter.assert_called_once_with(999)
    message.answer.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tasks_meta, has_next, expected_text, has_keyboard, has_next_button",
    [
        pytest.param([], False, "empty", False, False, id="empty_archive_no_navigation"),
        pytest.param(
            [1], False, "Your tasks list:", True, False, id="single_page_archive_no_next_arrow"
        ),
        pytest.param(
            [1], True, "Your tasks list", True, True, id="multi_page_archive_shows_next_arrow"
        ),
    ],
)
async def test_archive_paginator_should_render_correct_ui_states_based_on_backend_data(
    callback_query,
    state,
    message,
    mock_task_service,
    current_user,
    tasks_meta,
    has_next,
    expected_text,
    has_keyboard,
    has_next_button,
    fake_task,
):
    callback_data = TaskPaginatorCallBack(action=ActionsNav.ARCHIVE, page=1, is_archive=True)

    tasks = [fake_task for _ in tasks_meta]

    mock_task_service.get_tasks.return_value = (tasks, has_next)

    await pagination_archive_tasks(
        callback_query, callback_data, message, mock_task_service, current_user, state
    )

    mark_up = message.edit_text.call_args.kwargs["reply_markup"]

    assert (mark_up is not None) == has_keyboard

    actual_next_button_present = any(
        button.text == "➡️" for row in (mark_up.inline_keyboard if mark_up else []) for button in row
    )
    assert actual_next_button_present == has_next_button

    mock_task_service.get_tasks.assert_called_once_with(user_id=999, page=1, status=TodoStatus.DONE)
    message.edit_text.assert_called_once()
    callback_query.answer.assert_called_once()

    assert expected_text in message.edit_text.call_args.kwargs["text"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tasks_meta, has_next, expected_text, has_keyboard, has_next_button",
    [
        pytest.param([], False, "empty", False, False, id="empty_list_no_navigation"),
        pytest.param(
            [1], False, "Your tasks list:", True, False, id="single_page_list_no_next_arrow"
        ),
        pytest.param(
            [1], True, "Your tasks list", True, True, id="multi_page_list_shows_next_arrow"
        ),
    ],
)
async def test_active_tasks_paginator_should_render_correct_ui_states_based_on_backend_data(
    callback_query,
    state,
    message,
    mock_task_service,
    current_user,
    tasks_meta,
    has_next,
    expected_text,
    has_keyboard,
    has_next_button,
    fake_task,
):
    callback_data = TaskPaginatorCallBack(action=ActionsNav.LIST, page=1, is_archive=False)

    tasks = [fake_task for _ in tasks_meta]

    mock_task_service.get_tasks.return_value = (tasks, has_next)

    await pagination_tasks(
        callback_query, callback_data, mock_task_service, current_user, message, state
    )

    mark_up = message.edit_text.call_args.kwargs["reply_markup"]

    assert (mark_up is not None) == has_keyboard

    actual_next_button_present = any(
        button.text == "➡️" for row in (mark_up.inline_keyboard if mark_up else []) for button in row
    )
    assert actual_next_button_present == has_next_button

    mock_task_service.get_tasks.assert_called_once_with(
        user_id=999, page=1, status=TodoStatus.ACTIVE
    )
    message.edit_text.assert_called_once()
    callback_query.answer.assert_called_once()

    assert expected_text in message.edit_text.call_args.kwargs["text"]


@pytest.mark.asyncio
async def test_task_update_status_should_edit_task_status(
    callback_query, message, bot, state, current_user, mock_task_service, fake_task
):
    callback_data = TaskStatusCallback(new_status=TodoStatus.DONE, task_id=1, page=1)

    mock_task_service.update_task_by_id.return_value = fake_task

    await update_status(
        callback_query, callback_data, mock_task_service, current_user, message, bot, state
    )

    mock_task_service.update_task_by_id.assert_called_once()

    call_args = mock_task_service.update_task_by_id.call_args
    assert call_args.args[0] == 999
    assert call_args.args[1] == 1
    assert call_args.args[2].status == TodoStatus.DONE

    callback_query.answer.assert_called_once()


@pytest.mark.asyncio
async def test_task_deletion_should_delete_task_and_show_success_alert(
    callback_query, mock_task_service, current_user, message, state, fake_task
):
    callback_data = TaskViewCallback(action=ActionsView.DELETE, page=1, task_id=1)

    mock_task_service.get_tasks.return_value = (fake_task, False)
    await process_delete_task(
        callback_query, callback_data, mock_task_service, current_user, message, state
    )

    callback_kwargs = callback_query.answer.call_args_list[0].kwargs

    assert "deleted" in callback_kwargs["text"]
    assert not callback_kwargs["show_alert"]
    assert callback_query.answer.call_count == 2
