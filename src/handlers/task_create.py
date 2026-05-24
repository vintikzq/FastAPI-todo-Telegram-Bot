import contextlib
import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, ReplyKeyboardRemove, User
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram_calendar.schemas import SimpleCalAct

from src.keyboards.main_menu import get_main_menu_keyboard
from src.keyboards.task_menu import get_task_priority_buttons, skip_button
from src.schemas.callbacks import TaskFormCallBack, TaskPriorityCallback
from src.schemas.enums import MenuButtons
from src.schemas.tasks import TaskRequest
from src.services.tasks import TaskService
from src.states.tasks import CreateTaskState, UpdateTaskState

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("cancel"), StateFilter(CreateTaskState, UpdateTaskState))
async def cancel_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    msg_id = data.get("msg_id")

    if msg_id:
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text="❌ Operation canceled",
                reply_markup=None,
            )
        except TelegramBadRequest:
            logger.warning("Message modification skipped")
            pass

    await state.clear()
    await message.answer("Return to main menu", reply_markup=get_main_menu_keyboard())


@router.message(F.text == MenuButtons.CREATE_TASK)
async def start_task_creation(message: Message, state: FSMContext) -> None:
    await message.answer(text="Starting task creation", reply_markup=ReplyKeyboardRemove())

    sent_msg = await message.answer(
        "<b>Write task name:</b>\n\n<i>Type /cancel to cancel creation.</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[]),
        parse_mode="HTML",
    )

    await state.update_data(msg_id=sent_msg.message_id)
    await state.set_state(CreateTaskState.waiting_for_task_name)


@router.message(CreateTaskState.waiting_for_task_name)
async def process_task_name(message: Message, state: FSMContext, bot: Bot) -> None:

    await state.update_data(name=message.text)

    with contextlib.suppress(TelegramBadRequest):
        await message.delete()

    data = await state.get_data()

    msg_id = data.get("msg_id")
    try:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg_id,
            text="Name saved. Write task description:",
            reply_markup=skip_button(),
        )
    except TelegramBadRequest:
        logger.warning("Message modification skipped")
        pass

    await state.set_state(CreateTaskState.waiting_for_description)


@router.callback_query(
    CreateTaskState.waiting_for_description, TaskFormCallBack.filter(F.action == "skip")
)
async def process_task_description_skip(
    callback: CallbackQuery, state: FSMContext, callback_msg: Message
) -> None:

    await state.update_data(description=None)
    await callback.answer("Skipped")

    await callback_msg.edit_text(
        "Description skipped. Now select priority:", reply_markup=get_task_priority_buttons()
    )
    await state.set_state(CreateTaskState.waiting_for_task_priority)


@router.message(CreateTaskState.waiting_for_description)
async def process_task_description(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(description=message.text)

    with contextlib.suppress(TelegramBadRequest):
        await message.delete()

    data = await state.get_data()

    try:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data.get("msg_id"),
            text="Description saved. Now select priority:",
            reply_markup=get_task_priority_buttons(),
        )
    except TelegramBadRequest:
        logger.warning("Message modification skipped")
        pass

    await state.set_state(CreateTaskState.waiting_for_task_priority)


@router.callback_query(CreateTaskState.waiting_for_task_priority, TaskPriorityCallback.filter())
async def process_task_priority(
    callback: CallbackQuery,
    callback_msg: Message,
    callback_data: TaskPriorityCallback,
    state: FSMContext,
) -> None:
    await state.update_data(priority=callback_data.value)

    await callback.answer()

    await callback_msg.edit_text(
        "Priority saved. Now select deadline:", reply_markup=await SimpleCalendar().start_calendar()
    )

    await state.set_state(CreateTaskState.waiting_for_deadline_date)


@router.callback_query(SimpleCalendarCallback.filter(), CreateTaskState.waiting_for_deadline_date)
async def process_deadline(
    callback: CallbackQuery,
    callback_msg: Message,
    callback_data: SimpleCalendarCallback,
    state: FSMContext,
    task_service: TaskService,
    current_user: User,
) -> None:
    selected, date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        if not await is_deadline_correct(callback, callback_msg, date):
            return

        iso_date = date.isoformat()
        await state.update_data(due_date=iso_date)
        await complete_task_creation(state, task_service, current_user, callback_msg)

    elif callback_data.act == SimpleCalAct.cancel:
        await state.update_data(due_date=None)
        await complete_task_creation(state, task_service, current_user, callback_msg)


async def complete_task_creation(
    state: FSMContext, task_service: TaskService, current_user: User, callback_msg: Message
) -> None:
    data = await state.get_data()
    task_data = TaskRequest(**data)
    task = await task_service.create_task(current_user.id, task_data)
    await state.clear()
    await callback_msg.edit_text(text=task.format_to_html(), parse_mode="HTML")
    await callback_msg.answer("What's next?", reply_markup=get_main_menu_keyboard())


async def is_deadline_correct(
    callback: CallbackQuery, callback_msg: Message, date: datetime
) -> bool:
    if date.date() < datetime.now().date():
        await callback.answer("The deadline cannot be in the past!", show_alert=True)
        await callback_msg.edit_text(
            "Invalid date! Please select a future date for the deadline",
            reply_markup=await SimpleCalendar().start_calendar(),
        )
        return False
    return True
