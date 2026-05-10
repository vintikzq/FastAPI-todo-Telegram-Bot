import asyncio

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, User
import httpx

from src.keyboards.task_menu import get_navigation_buttons, get_task_buttons
from src.schemas.callbacks import TaskPaginatorCallBack, TaskViewCallback
from src.schemas.enums import ActionsNav, ActionsView, MenuButtons
from src.services.tasks import TaskService


router = Router()


@router.message(F.text == MenuButtons.MY_TASKS)
async def get_all_tasks(
        message: Message,
        task_service: TaskService,
        current_user: User,
):
    await render_tasks_list(message, task_service=task_service,
                            user_id=current_user.id, current_page=1)


@router.callback_query(TaskPaginatorCallBack.filter(F.action.in_((ActionsNav.PAGE_DOWN, ActionsNav.PAGE_UP, ActionsNav.LIST))))
async def pagination_tasks(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message
):
    current_page = callback_data.page
    await render_tasks_list(callback_msg, task_service, current_user.id, current_page=current_page)

    await callback.answer()


@router.callback_query(TaskPaginatorCallBack.filter(F.action == ActionsNav.VIEW))
async def task_view(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message
):
    current_page = callback_data.page
    task_id = callback_data.task_id
    if task_id:
        try:
            task = await task_service.get_task_by_id(
                user_id=current_user.id,
                task_id=task_id
            )

            await callback_msg.edit_text(
                text=task.format_to_html(),
                reply_markup=get_task_buttons(
                    task_id, current_page=current_page),
                parse_mode='HTML')
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
    if task_id:
        await task_service.delete_task_by_id(
            current_user.id,
            task_id=task_id
        )

        await callback.answer(
            text="✅ Task successfully deleted",
            show_alert=False
        )

        current_page = callback_data.page or 1

    await render_tasks_list(callback_msg, task_service, current_user.id, current_page=current_page)

    await callback.answer()


async def render_tasks_list(
    event: Message | CallbackQuery,
    task_service: TaskService,
    user_id: int,
    current_page: int,
):
    tasks, meta = await task_service.get_tasks(user_id=user_id, page=current_page)

    if not tasks and current_page > 1:
        return await render_tasks_list(event, task_service, user_id, current_page - 1)

    text = "Your tasks list:" if tasks else "Your task list is empty now!"
    kb = get_navigation_buttons(
        tasks=tasks, current_page=current_page, has_next=meta) if tasks else None

    if isinstance(event, Message):
        await event.answer(text=text, reply_markup=kb, parse_mode='HTML')
    else:
        if isinstance(event.message, Message):
            await event.message.edit_text(text=text, reply_markup=kb, parse_mode='HTML')


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
