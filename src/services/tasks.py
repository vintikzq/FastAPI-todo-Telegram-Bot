from httpx import AsyncClient
import httpx

from src.schemas.tasks import TaskResponse
from src.services.base import BaseClient
from src.storage.tokens import TokenStorage


class TaskService(BaseClient):
    def __init__(self, session: AsyncClient, token_storage: TokenStorage) -> None:
        super().__init__(session)
        self.token_storage = token_storage

    async def get_tasks(self, user_id):
        token = await self.token_storage.get_token(user_id)
        try:
            data = await self._make_request('get', '/tasks', headers={'Authorization': f"Bearer {token}"})
            return [TaskResponse(**task) for task in data]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                await self.token_storage.delete_token(user_id)
            raise e
