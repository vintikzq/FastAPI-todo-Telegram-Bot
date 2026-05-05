from src.services.base import BaseClient


class TaskService(BaseClient):
    async def get_tasks(self):
        await self._make_request('get', '/tasks')
