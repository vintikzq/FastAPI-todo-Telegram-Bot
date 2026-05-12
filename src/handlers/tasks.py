from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, Message, User
import httpx

from src.keyboards.main_menu import get_main_menu_keyboard
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
):
    await render_tasks_list(message, task_service=task_service,
                            user_id=current_user.id, current_page=1, is_edit=False)


@router.callback_query(TaskPaginatorCallBack.filter(F.action.in_((ActionsNav.PAGE_DOWN, ActionsNav.PAGE_UP, ActionsNav.LIST))))
async def pagination_tasks(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message
):
    current_page = callback_data.page
    await render_tasks_list(callback_msg, task_service, current_user.id, current_page=current_page, is_edit=True)

    await callback.answer()


@router.callback_query(TaskPaginatorCallBack.filter(F.action == ActionsNav.VIEW))
async def task_view(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message,
    bot: Bot
):
    task_id = callback_data.task_id
    if task_id:
        try:
            task = await task_service.get_task_by_id(
                user_id=current_user.id,
                task_id=task_id
            )

            await render_task_card(
                bot=bot,
                page=callback_data.page,
                callback_msg=callback_msg,
                task=task,
                status=task.status)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                await callback_msg.edit_text(text="Task not found")
    await callback.answer()


@router.callback_query(TaskViewCallback.filter(F.action == ActionsView.DELETE))
async def process_delete_task(
    callback: CallbackQuery,
    callback_data: TaskViewCallback,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message
):
    task_id = callback_data.task_id
    current_page = callback_data.page or 1

    if task_id:
        await task_service.delete_task_by_id(
            current_user.id,
            task_id=task_id
        )

        await callback.answer(
            text="✅ Task successfully deleted",
            show_alert=False
        )

    await render_tasks_list(callback_msg, task_service, current_user.id, current_page=current_page, is_edit=True)

    await callback.answer()


@router.callback_query(TaskStatusCallback.filter())
async def update_status(
    callback: CallbackQuery,
    callback_data: TaskStatusCallback,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message,
    bot: Bot
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
        status=updated_task.status)

    await callback.answer()


@router.callback_query(F.data == 'go_to_menu')
async def go_to_main_menu(
    callback: CallbackQuery,
    callback_msg: Message
):
    await callback_msg.answer(text="Returned to main menu",
                              reply_markup=get_main_menu_keyboard())

    callback.answer()


async def render_tasks_list(
    message: Message,
    task_service: TaskService,
    user_id: int,
    current_page: int,
    is_edit: bool = False
):
    tasks, meta = await task_service.get_tasks(user_id=user_id, page=current_page)

    if not tasks and current_page > 1:
        return await render_tasks_list(message, task_service, user_id, current_page - 1, is_edit=True)

    text = "Your tasks list:" if tasks else "Your task list is empty now!"
    kb = get_navigation_buttons(
        tasks=tasks, current_page=current_page, has_next=meta) if tasks else None

    if is_edit:
        await message.edit_text(text=text, reply_markup=kb, parse_mode='HTML')
    else:
        await message.answer(text=text, reply_markup=kb, parse_mode='HTML')


async def render_task_card(
    page: int,
    callback_msg: Message,
    task: TaskResponse,
    status: TodoStatus,
    bot: Bot,
    msg_id: int | None = None,
    chat_id: int | None = None
):
    if msg_id is None:
        await callback_msg.edit_text(
            text=task.format_to_html(),
            reply_markup=get_task_buttons(
                task_id=task.id,
                current_page=page,
                status=status),
            parse_mode='HTML'
        )
    else:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text=task.format_to_html(),
            reply_markup=get_task_buttons(
                task_id=task.id,
                current_page=page,
                status=status),
            parse_mode='HTML'
        )


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
