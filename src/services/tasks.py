from typing import Any

from httpx import AsyncClient

from src.schemas.enums import TodoStatus
from src.schemas.tasks import TaskRequest, TaskResponse, TaskStatsResponse, TaskUpdateRequest
from src.services.base import BaseClient
from src.storage.tokens import TokenStorage


class TaskService(BaseClient):
    """
    Business logic gateway for task CRUD operations.

    Transforms raw API payload into domain DTOs and handles edge-case pagination.
    """

    def __init__(self, session: AsyncClient, token_storage: TokenStorage) -> None:
        super().__init__(session, token_storage)
        self.token_storage = token_storage

    async def get_tasks(
        self, user_id: int, page: int = 1, limit: int = 5, status: TodoStatus | None = None
    ) -> tuple[list[TaskResponse], bool]:
        offset = (page - 1) * limit
        params: dict[str, Any] = {"limit": limit + 1, "offset": offset}

        if status is not None:
            params["status"] = status

        data = await self._make_request("get", "/tasks", user_id, params=params)
        if len(data) > limit:
            return ([TaskResponse(**task) for task in data[:limit]], True)
        return ([TaskResponse(**task) for task in data], False)

    async def create_task(self, user_id: int, data: TaskRequest) -> TaskResponse:
        task = await self._make_request("post", "/tasks", user_id, data=data.model_dump())
        return TaskResponse(**task)

    async def get_task_by_id(self, user_id: int, task_id: int) -> TaskResponse:
        data = await self._make_request("get", f"/tasks/{task_id}", user_id)
        return TaskResponse(**data)

    async def delete_task_by_id(self, user_id: int, task_id: int) -> None:
        await self._make_request("delete", f"/tasks/{task_id}", user_id)

    async def update_task_by_id(
        self, user_id: int, task_id: int, data: TaskUpdateRequest
    ) -> TaskResponse:
        task = await self._make_request(
            "patch", f"/tasks/{task_id}", user_id, data=data.model_dump(exclude_unset=True)
        )
        return TaskResponse(**task)

    async def get_stats_counter(self, user_id: int) -> TaskStatsResponse:
        tasks_stats = await self._make_request("get", "/tasks/stats", user_id)

        return TaskStatsResponse(**tasks_stats)
