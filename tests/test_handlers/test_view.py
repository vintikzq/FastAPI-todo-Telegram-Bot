import pytest

from src.handlers.archive_tasks import pagination_archive_tasks
from src.handlers.common import stats_handler
from src.schemas.callbacks import TaskPaginatorCallBack
from src.schemas.enums import ActionsNav, MenuButtons, TodoStatus


@pytest.mark.asyncio
async def test_stats_handler_should_delete_previous_keyboard_and_write_user_stats(
    state, bot, task_service,
    message, fake_stats_response,
    current_user
):
    await state.update_data(last_msg_id=111)
    message.text = MenuButtons.STATS
    task_service.get_stats_counter.return_value = fake_stats_response

    await stats_handler(message, task_service, current_user, bot, state)

    assert message.answer.call_args.kwargs['reply_markup'] is not None

    assert "Tasks at work" in message.answer.call_args.kwargs['text']
    bot.edit_message_reply_markup.assert_called_once_with(
        chat_id=message.chat.id,
        message_id=111,
        reply_markup=None
    )

    task_service.get_stats_counter.assert_called_once_with(999)
    message.answer.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tasks_meta, has_next, expected_text, has_keyboard, has_next_button",
    [
        pytest.param([], False, 'empty', False, False,
                     id="empty_archive_no_navigation"),
        pytest.param([1], False, "Your tasks list:", True, False,
                     id="single_page_archive_no_next_arrow"),
        pytest.param([1], True, "Your tasks list", True, True,
                     id="multi_page_archive_shows_next_arrow")
    ]
)
async def test_archive_paginator_should_render_correct_ui_states_based_on_backend_data(
    callback_query, state,
    message, task_service,
    current_user, tasks_meta,
    has_next, expected_text,
    has_keyboard, has_next_button,
    fake_task
):
    callback_data = TaskPaginatorCallBack(
        action=ActionsNav.ARCHIVE, page=1, is_archive=True)

    tasks = [fake_task for _ in tasks_meta]

    task_service.get_tasks.return_value = (tasks, has_next)

    await pagination_archive_tasks(
        callback_query, callback_data,
        message, task_service,
        current_user, state
    )

    mark_up = message.edit_text.call_args.kwargs['reply_markup']

    assert (mark_up is not None) == has_keyboard

    actual_next_btn_present = any(
        button.text == '➡️'
        for row in (mark_up.inline_keyboard if mark_up else [])
        for button in row
    )
    assert actual_next_btn_present == has_next_button

    task_service.get_tasks.assert_called_once_with(
        user_id=999, page=1, status=TodoStatus.DONE)
    message.edit_text.assert_called_once()
    callback_query.answer.assert_called_once()

    assert expected_text in message.edit_text.call_args.kwargs['text']
