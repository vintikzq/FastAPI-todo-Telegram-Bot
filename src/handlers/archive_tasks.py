from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from src.handlers.tasks import render_tasks_list
from src.schemas.callbacks import TaskPaginatorCallBack
from src.schemas.enums import ActionsNav, TodoStatus
from src.services.tasks import TaskService


router = Router()


@router.callback_query(TaskPaginatorCallBack.filter(F.action == ActionsNav.ARCHIVE))
async def pagination_archive_tasks(
    callback: CallbackQuery,
    callback_data: TaskPaginatorCallBack,
    callback_msg: Message,
    task_service: TaskService,
    current_user: User,
    state: FSMContext
):
    page = callback_data.page

    await render_tasks_list(
        message=callback_msg,
        task_service=task_service,
        user_id=current_user.id,
        current_page=page,
        state=state,
        is_edit=True,
        status=TodoStatus.DONE
    )

    await callback.answer()
