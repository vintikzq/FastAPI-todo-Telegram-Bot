from httpx import AsyncClient
import httpx

from src.schemas.tasks import TaskRequest, TaskResponse
from src.services.base import BaseClient
from src.storage.tokens import TokenStorage


class TaskService(BaseClient):
    def __init__(self, session: AsyncClient, token_storage: TokenStorage) -> None:
        super().__init__(session, token_storage)
        self.token_storage = token_storage

    async def get_tasks(self, user_id: int) -> list[TaskResponse]:
        token = await self.token_storage.get_token(user_id)

        data = await self._make_request('get', '/tasks', user_id, headers={'Authorization': f"Bearer {token}"})
        return [TaskResponse(**task) for task in data]

    async def create_task(self, user_id: int, data: TaskRequest) -> TaskResponse:
        token = await self.token_storage.get_token(user_id)
        task = await self._make_request('post', '/tasks', user_id, headers={'Authorization': f"Bearer {token}"}, data=data.model_dump())
        return TaskResponse(**task)
