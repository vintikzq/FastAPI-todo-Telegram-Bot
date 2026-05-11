from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, User
import httpx

from src.handlers.tasks import render_task_card
from src.keyboards.update_menu import get_update_buttons
from src.schemas.callbacks import TaskUpdateCallback, TaskViewCallback
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
    await callback_msg.edit_text(
        text="Select fields to edit:",
        reply_markup=get_update_buttons(
            task_id=callback_data.task_id,
            page=callback_data.page
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
        page=callback_data.page
    )
    tmp_msg = await callback_msg.answer(text="Switching to edit mode...", reply_markup=ReplyKeyboardRemove())
    await tmp_msg.delete()

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

    try:
        await message.delete()
    except:
        pass

    try:
        updated_task = await task_service.update_task_by_id(
            user_id=current_user.id,
            task_id=task_id,
            data=TaskUpdateRequest(name=message.text)
        )

        await render_task_card(
            chat_id=message.chat.id,
            bot=bot,
            page=page,
            callback_msg=message,
            task=updated_task,
            status=updated_task.status,
            msg_id=msg_id
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await bot.edit_message_text(message_id=msg_id, text="Task not found")
    finally:
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
        page=callback_data.page
    )
    tmp_msg = await callback_msg.answer(text="Switching to edit mode...", reply_markup=ReplyKeyboardRemove())
    await tmp_msg.delete()

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

    try:
        await message.delete()
    except:
        pass

    try:
        updated_task = await task_service.update_task_by_id(
            user_id=current_user.id,
            task_id=task_id,
            data=TaskUpdateRequest(description=message.text)
        )

        await render_task_card(
            chat_id=message.chat.id,
            bot=bot,
            page=page,
            callback_msg=message,
            task=updated_task,
            status=updated_task.status,
            msg_id=msg_id
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            await bot.edit_message_text(message_id=msg_id, text="Task not found")
    finally:
        await state.clear()
