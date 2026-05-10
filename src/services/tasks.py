from httpx import AsyncClient

from src.schemas.tasks import TaskRequest, TaskResponse, TaskUpdateRequest
from src.services.base import BaseClient
from src.storage.tokens import TokenStorage


class TaskService(BaseClient):
    def __init__(self, session: AsyncClient, token_storage: TokenStorage) -> None:
        super().__init__(session, token_storage)
        self.token_storage = token_storage

    async def get_tasks(self, user_id: int, page: int = 1, limit: int = 5) -> tuple[list[TaskResponse], bool]:
        offset = (page - 1) * limit
        data = await self._make_request(
            'get', '/tasks', user_id, params={'limit': limit + 1, 'offset': offset})
        if len(data) > limit:
            return ([TaskResponse(**task) for task in data[:limit]], True)
        return ([TaskResponse(**task) for task in data], False)

    async def create_task(self, user_id: int, data: TaskRequest) -> TaskResponse:
        task = await self._make_request('post', '/tasks', user_id, data=data.model_dump())
        return TaskResponse(**task)

    async def get_task_by_id(self, user_id: int, task_id: int) -> TaskResponse:
        data = await self._make_request('get', f'/tasks/{task_id}', user_id)
        return TaskResponse(**data)

    async def delete_task_by_id(self, user_id: int, task_id: int):
        await self._make_request('delete', f'/tasks/{task_id}', user_id)
