from aiogram import F, Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct

from src.handlers.task_create import is_deadline_correct
from src.handlers.tasks import render_task_card
from src.keyboards.task_menu import get_task_priority_buttons
from src.keyboards.update_menu import get_update_buttons
from src.schemas.callbacks import TaskPriorityCallback, TaskUpdateCallback, TaskViewCallback
from src.schemas.enums import ActionsUpdate, ActionsView
from src.schemas.tasks import TaskUpdateRequest
from src.services.tasks import TaskService
from src.states.tasks import UpdateTaskState

router = Router()


@router.callback_query(TaskViewCallback.filter(F.action == ActionsView.UPDATE))
async def process_update_menu(
    callback: CallbackQuery,
    callback_data: TaskViewCallback,
    callback_msg: Message
):
    is_archive = callback_data.is_archive

    await callback_msg.edit_text(
        text="Select fields to edit:",
        reply_markup=get_update_buttons(
            task_id=callback_data.task_id,
            page=callback_data.page,
            is_archive=is_archive
        )
    )

    await callback.answer()


@router.callback_query(TaskUpdateCallback.filter(F.to_update == ActionsUpdate.NAME))
async def change_task_name(
    callback: CallbackQuery,
    callback_data: TaskUpdateCallback,
    callback_msg: Message,
    state: FSMContext
):

    await state.update_data(
        msg_id=callback_msg.message_id,
        task_id=callback_data.task_id,
        page=callback_data.page,
        is_archive=callback_data.is_archive
    )

    await callback_msg.edit_text(text="<b>Write new task name:</b>\n\n"
                                 "<i>Type /cancel to stop the update.</i>",
                                 parse_mode='HTML',
                                 reply_markup=None)

    await state.set_state(UpdateTaskState.waiting_for_new_task_name)

    await callback.answer()


@router.message(UpdateTaskState.waiting_for_new_task_name)
async def process_new_task_name(
    message: Message,
    task_service: TaskService,
    current_user: User,
    bot: Bot,
    state: FSMContext
):
    data = await state.get_data()

    task_id = data['task_id']
    page = data['page']
    msg_id = data['msg_id']
    is_archive = data['is_archive']

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    updated_task = await task_service.update_task_by_id(
        user_id=current_user.id,
        task_id=task_id,
        data=TaskUpdateRequest(name=message.text)
    )

    await render_task_card(
        msg_id=msg_id,
        chat_id=message.chat.id,
        bot=bot,
        page=page,
        callback_msg=message,
        task=updated_task,
        status=updated_task.status,
        state=state,
        is_archive=is_archive
    )

    await state.clear()


@router.callback_query(TaskUpdateCallback.filter(F.to_update == ActionsUpdate.DESCRIPTION))
async def change_task_description(
    callback: CallbackQuery,
    callback_data: TaskUpdateCallback,
    callback_msg: Message,
    state: FSMContext
):

    await state.update_data(
        msg_id=callback_msg.message_id,
        task_id=callback_data.task_id,
        page=callback_data.page,
        is_archive=callback_data.is_archive
    )

    await callback_msg.edit_text(text="<b>Write new task description:</b>\n\n"
                                 "<i>Type /cancel to stop the update.</i>",
                                 parse_mode='HTML',
                                 reply_markup=None)

    await state.set_state(UpdateTaskState.waiting_for_new_description)

    await callback.answer()


@router.message(UpdateTaskState.waiting_for_new_description)
async def process_new_task_description(
    message: Message,
    task_service: TaskService,
    current_user: User,
    bot: Bot,
    state: FSMContext
):
    data = await state.get_data()

    task_id = data['task_id']
    page = data['page']
    msg_id = data['msg_id']
    is_archive = data['is_archive']

    try:
        await message.delete()
    except TelegramBadRequest:
        pass

    updated_task = await task_service.update_task_by_id(
        user_id=current_user.id,
        task_id=task_id,
        data=TaskUpdateRequest(description=message.text)
    )

    await render_task_card(
        msg_id=msg_id,
        chat_id=message.chat.id,
        bot=bot,
        page=page,
        callback_msg=message,
        task=updated_task,
        status=updated_task.status,
        state=state,
        is_archive=is_archive
    )

    await state.clear()


@router.callback_query(TaskUpdateCallback.filter(F.to_update == ActionsUpdate.PRIORITY))
async def change_task_priority(
    callback: CallbackQuery,
    callback_data: TaskUpdateCallback,
    callback_msg: Message,
    state: FSMContext
):

    await state.update_data(
        msg_id=callback_msg.message_id,
        task_id=callback_data.task_id,
        page=callback_data.page,
        is_archive=callback_data.is_archive
    )

    await callback_msg.edit_text(text="<b>Select new task priority:</b>\n\n"
                                 "<i>Type /cancel to stop the update.</i>",
                                 parse_mode='HTML',
                                 reply_markup=get_task_priority_buttons())

    await state.set_state(UpdateTaskState.waiting_for_new_task_priority)

    await callback.answer()


@router.callback_query(TaskPriorityCallback.filter(), UpdateTaskState.waiting_for_new_task_priority)
async def process_new_task_priority(
    callback: CallbackQuery,
    callback_data: TaskPriorityCallback,
    callback_msg: Message,
    task_service: TaskService,
    current_user: User,
    bot: Bot,
    state: FSMContext
):
    data = await state.get_data()

    task_id = data['task_id']
    page = data['page']
    msg_id = data['msg_id']
    is_archive = data['is_archive']

    updated_task = await task_service.update_task_by_id(
        user_id=current_user.id,
        task_id=task_id,
        data=TaskUpdateRequest(priority=callback_data.value)
    )

    await render_task_card(
        msg_id=msg_id,
        chat_id=callback_msg.chat.id,
        bot=bot,
        page=page,
        callback_msg=callback_msg,
        task=updated_task,
        status=updated_task.status,
        state=state,
        is_archive=is_archive
    )

    await state.clear()


@router.callback_query(TaskUpdateCallback.filter(F.to_update == ActionsUpdate.DEADLINE))
async def change_task_deadline(
    callback: CallbackQuery,
    callback_data: TaskUpdateCallback,
    callback_msg: Message,
    state: FSMContext
):

    await state.update_data(
        msg_id=callback_msg.message_id,
        task_id=callback_data.task_id,
        page=callback_data.page,
        is_archive=callback_data.is_archive
    )

    await callback_msg.edit_text(text="<b>Select new task deadline:</b>\n\n"
                                 "<i>Type /cancel to stop the update.</i>",
                                 parse_mode='HTML',
                                 reply_markup=await SimpleCalendar().start_calendar())

    await state.set_state(UpdateTaskState.waiting_for_new_deadline_date)

    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), UpdateTaskState.waiting_for_new_deadline_date)
async def process_new_deadline(
    callback: CallbackQuery,
    callback_data: SimpleCalendarCallback,
    callback_msg: Message,
    task_service: TaskService,
    current_user: User,
    bot: Bot,
    state: FSMContext
):
    data = await state.get_data()

    task_id = data['task_id']
    page = data['page']
    msg_id = data['msg_id']
    is_archive = data['is_archive']

    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        if not await is_deadline_correct(callback, callback_msg, date):
            return

        iso_date = date.isoformat()
        updated_task = await task_service.update_task_by_id(
            user_id=current_user.id,
            task_id=task_id,
            data=TaskUpdateRequest(due_date=iso_date))

        await render_task_card(
            msg_id=msg_id,
            chat_id=callback_msg.chat.id,
            bot=bot,
            page=page,
            callback_msg=callback_msg,
            task=updated_task,
            status=updated_task.status,
            state=state,
            is_archive=is_archive
        )
        await state.clear()

    elif callback_data.act == SimpleCalAct.cancel:
        updated_task = await task_service.update_task_by_id(
            user_id=current_user.id,
            task_id=task_id,
            data=TaskUpdateRequest(due_date=None))

        await render_task_card(
            msg_id=msg_id,
            chat_id=callback_msg.chat.id,
            bot=bot,
            page=page,
            callback_msg=callback_msg,
            task=updated_task,
            status=updated_task.status,
            state=state,
            is_archive=is_archive
        )
        await state.clear()
