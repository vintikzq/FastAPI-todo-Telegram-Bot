from aiogram import F, Router
from aiogram.types import Message, User


from src.schemas.enums import MenuButtons
from src.services.tasks import TaskService


router = Router()


@router.message(F.text == MenuButtons.MY_TASKS)
async def get_all_tasks(message: Message, task_service: TaskService, current_user: User):
    try:
        res = await task_service.get_tasks(current_user.id)
        if res:
            messages = [task.format_to_html() for task in res]
            await message.answer("\n".join(messages), parse_mode='HTML')
        if not res:
            await message.answer("Your tasks list is empty now!")
    except Exception:
        await message.answer("Something went wrong. Try later.")
