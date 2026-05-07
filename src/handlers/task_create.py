from datetime import datetime
import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, User
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct
import httpx
from pydantic import ValidationError

from src.keyboards.main_menu import get_main_menu_keyboard
from src.keyboards.task_menu import create_task_priority_buttons, skip_button
from src.schemas.callbacks import TaskFormCallBack, TaskPriorityCallback
from src.schemas.enums import MenuButtons
from src.schemas.tasks import TaskRequest
from src.services.tasks import TaskService
from src.states.tasks import CreateTaskState

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('cancel'), StateFilter(CreateTaskState))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Task creation successfully canceled",
                         reply_markup=get_main_menu_keyboard())


@router.message(F.text == MenuButtons.CREATE_TASK)
async def start_task_creation(message: Message, state: FSMContext):
    await message.answer("<b>Write task name:</b>\n\n"
                         "<i>Type /cancel to cancel creation.</i>",
                         reply_markup=ReplyKeyboardRemove(),
                         parse_mode="HTML")
    await state.set_state(CreateTaskState.waiting_for_task_name)


@router.message(CreateTaskState.waiting_for_task_name)
async def process_task_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    sent_msg = await message.answer(
        f"Name saved. Write task description:",
        reply_markup=skip_button())
    await state.update_data(last_msg_id=sent_msg.message_id)
    await state.set_state(CreateTaskState.waiting_for_description)


@router.callback_query(CreateTaskState.waiting_for_description, TaskFormCallBack.filter(F.action == 'skip'))
async def process_task_description_skip(
        callback: CallbackQuery,
        state: FSMContext,
        callback_msg: Message):

    await state.update_data(description=None)
    await callback.answer(f"Пропущено")

    await callback_msg.edit_text(
        "Description skipped. Now select priority:",
        reply_markup=create_task_priority_buttons()
    )
    await state.set_state(CreateTaskState.waiting_for_task_priority)


@router.message(CreateTaskState.waiting_for_description)
async def process_task_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "Description saved. Now select priority:",
        reply_markup=create_task_priority_buttons()
    )
    data = await state.get_data()
    if message.bot is not None:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=data.get('last_msg_id'),
            reply_markup=None
        )
    await state.set_state(CreateTaskState.waiting_for_task_priority)


@router.callback_query(CreateTaskState.waiting_for_task_priority, TaskPriorityCallback.filter())
async def process_task_priority(
    callback: CallbackQuery,
    callback_msg: Message,
    callback_data: TaskPriorityCallback,
    state: FSMContext
):
    await state.update_data(priority=callback_data.value)

    await callback.answer()

    await callback_msg.edit_text(
        f"Priority saved. Now select deadline:",
        reply_markup=await SimpleCalendar().start_calendar()
    )

    await state.set_state(CreateTaskState.waiting_for_deadline_date)


@router.callback_query(SimpleCalendarCallback.filter())
async def process_deadline(
    callback: CallbackQuery,
    callback_msg: Message,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
    task_service: TaskService,
    current_user: User
):
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        if date.date() < datetime.now().date():
            await callback.answer("The deadline cannot be in the past!", show_alert=True)
            await callback_msg.edit_text(
                "Invalid date! Please select a future date for the deadline",
                reply_markup=await SimpleCalendar().start_calendar()
            )
            return
        iso_date = date.isoformat()
        await state.update_data(due_date=iso_date)
        await complete_task_creation(state, task_service,
                                     current_user, callback_msg)

    elif callback_data.act == SimpleCalAct.cancel:
        await state.update_data(due_date=None)
        await complete_task_creation(state, task_service,
                                     current_user, callback_msg)


async def complete_task_creation(
    state: FSMContext,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message
):
    try:
        data = await state.get_data()
        task_data = TaskRequest(**data)
        task = await task_service.create_task(current_user.id, task_data)
        await state.clear()
        await callback_msg.edit_text(text=task.format_to_html(), parse_mode='HTML')
        await callback_msg.answer("What's next?",
                                  reply_markup=get_main_menu_keyboard())
    except ValidationError:
        await state.clear()
        await callback_msg.answer("Data is invalid")
    except httpx.ConnectError:
        await callback_msg.answer("Check your connection and try again.")
    except httpx.HTTPStatusError:
        await callback_msg.answer("Something went wrong on our end. Please try later.")
