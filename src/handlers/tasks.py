from aiogram import F, Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from src.keyboards.task_menu import get_navigation_buttons, get_task_buttons
from src.schemas.callbacks import TaskPaginatorCallBack, TaskStatusCallback, TaskViewCallback
from src.schemas.enums import ActionsNav, ActionsView, MenuButtons, TodoStatus
from src.schemas.tasks import TaskResponse, TaskUpdateRequest
from src.services.tasks import TaskService


router = Router()


@router.message(F.text == MenuButtons.MY_TASKS)
async def get_all_tasks(
        message: Message,
        task_service: TaskService,
        current_user: User,
        state: FSMContext,
        bot: Bot
):

    data = await state.get_data()
    msg_id = data.get('last_msg_id')

    try:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=msg_id,
            reply_markup=None
        )
    except TelegramBadRequest:
        pass

    await render_tasks_list(
        message, task_service=task_service,
        user_id=current_user.id, current_page=1,
        is_edit=False, status=TodoStatus.ACTIVE,
        state=state
    )


@router.callback_query(TaskPaginatorCallBack.filter(F.action.in_((ActionsNav.PAGE_DOWN, ActionsNav.PAGE_UP, ActionsNav.LIST))))
async def pagination_tasks(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message,
    state: FSMContext,
    status: TodoStatus | None = None
):
    current_page = callback_data.page

    if callback_data.is_archive:
        status = TodoStatus.DONE
    else:
        status = TodoStatus.ACTIVE

    await render_tasks_list(
        callback_msg,
        task_service,
        current_user.id,
        current_page=current_page,
        status=status,
        is_edit=True,
        state=state
    )

    await callback.answer()


@router.callback_query(TaskPaginatorCallBack.filter(F.action == ActionsNav.VIEW))
async def task_view(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message,
    bot: Bot,
    state: FSMContext
):
    task_id = callback_data.task_id
    if task_id:
        task = await task_service.get_task_by_id(
            user_id=current_user.id,
            task_id=task_id
        )
        is_archive = callback_data.is_archive

        await render_task_card(
            bot=bot,
            page=callback_data.page,
            callback_msg=callback_msg,
            task=task,
            status=task.status,
            is_archive=is_archive,
            state=state)

    await callback.answer()


@router.callback_query(TaskViewCallback.filter(F.action == ActionsView.DELETE))
async def process_delete_task(
    callback: CallbackQuery,
    callback_data: TaskViewCallback,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message,
    state: FSMContext
):
    task_id = callback_data.task_id
    current_page = callback_data.page or 1
    is_archive = callback_data.is_archive

    if task_id:
        await task_service.delete_task_by_id(
            current_user.id,
            task_id=task_id
        )

        await callback.answer(
            text="✅ Task successfully deleted",
            show_alert=False
        )

    status = TodoStatus.DONE if is_archive else TodoStatus.ACTIVE

    await render_tasks_list(
        callback_msg,
        task_service,
        current_user.id,
        current_page=current_page,
        is_edit=True,
        state=state,
        status=status,
        is_archive=is_archive
    )

    await callback.answer()


@router.callback_query(TaskStatusCallback.filter())
async def update_status(
    callback: CallbackQuery,
    callback_data: TaskStatusCallback,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message,
    bot: Bot,
    state: FSMContext
):
    task_id = callback_data.task_id

    user_id = current_user.id

    new_status = callback_data.new_status

    payload = TaskUpdateRequest(status=new_status)

    updated_task = await task_service.update_task_by_id(user_id, task_id, payload)

    await render_task_card(
        bot=bot,
        page=callback_data.page,
        callback_msg=callback_msg,
        task=updated_task,
        status=updated_task.status,
        state=state,
        is_archive=callback_data.is_archive)

    await callback.answer()


async def render_tasks_list(
    message: Message,
    task_service: TaskService,
    user_id: int,
    current_page: int,
    state: FSMContext,
    status: TodoStatus | None = None,
    is_edit: bool = False,
    is_archive: bool = False

):
    tasks, meta = await task_service.get_tasks(user_id=user_id, page=current_page, status=status)

    if not tasks and current_page > 1:
        return await render_tasks_list(message, task_service, user_id, current_page - 1, is_edit=True, state=state, is_archive=is_archive)

    text = "Your tasks list:" if tasks else "Your task list is empty now!"

    kb = get_navigation_buttons(
        tasks=tasks, current_page=current_page, has_next=meta, is_archive=is_archive) if tasks else None

    if is_edit:
        try:
            sent_msg = await message.edit_text(text=text, reply_markup=kb, parse_mode='HTML')
        except TelegramBadRequest as e:

            if "message is not modified" in e.message:
                pass
            else:
                raise e

    else:
        sent_msg = await message.answer(text=text, reply_markup=kb, parse_mode='HTML')

    if isinstance(sent_msg, Message) and kb is not None:
        await state.update_data(last_msg_id=sent_msg.message_id)


async def render_task_card(
    page: int,
    callback_msg: Message,
    task: TaskResponse,
    status: TodoStatus,
    bot: Bot,
    state: FSMContext,
    is_archive: bool = False,
    msg_id: int | None = None,
    chat_id: int | None = None
):
    if msg_id is None:
        try:
            sent_msg = await callback_msg.edit_text(
                text=task.format_to_html(),
                reply_markup=get_task_buttons(
                    task_id=task.id,
                    current_page=page,
                    status=status,
                    is_archive=is_archive),
                parse_mode='HTML'
            )
        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                pass
            else:
                raise e

        if isinstance(sent_msg, Message):
            await state.update_data(last_msg_id=sent_msg.message_id)

    else:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=task.format_to_html(),
                reply_markup=get_task_buttons(
                    task_id=task.id,
                    current_page=page,
                    status=status,
                    is_archive=is_archive),
                parse_mode='HTML'
            )
        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                pass
            else:
                raise e
        await state.update_data(last_msg_id=msg_id)


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
