from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, User
import httpx

from src.keyboards.task_menu import get_navigation_buttons, get_task_buttons
from src.schemas.callbacks import TaskPaginatorCallBack
from src.schemas.enums import ActionsNav, MenuButtons
from src.services.tasks import TaskService


router = Router()


@router.message(F.text == MenuButtons.MY_TASKS)
async def get_all_tasks(
        message: Message,
        task_service: TaskService,
        current_user: User):

    tasks, meta = await task_service.get_tasks(user_id=current_user.id)

    has_next = meta

    current_page = 1

    if tasks:
        await message.answer(text="Your tasks list:", reply_markup=get_navigation_buttons(
            tasks=tasks,
            current_page=current_page,
            has_next=has_next))
    else:
        await message.answer(text="Your task list is empty now!")


@router.callback_query(TaskPaginatorCallBack.filter(F.action.in_((ActionsNav.PAGE_DOWN, ActionsNav.PAGE_UP, ActionsNav.LIST))))
async def pagination_tasks(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    task_service: TaskService,
    current_user: User,
    callback_msg: Message
):
    current_page = callback_data.page
    tasks, meta = await task_service.get_tasks(user_id=current_user.id, page=current_page)

    has_next = meta

    if tasks:
        await callback_msg.edit_text(
            text="Your tasks list:",
            reply_markup=get_navigation_buttons(
                tasks=tasks,
                current_page=current_page,
                has_next=has_next),
            parse_mode='HTML')
    else:
        await callback_msg.edit_text(text="Your task list is empty now!")

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
