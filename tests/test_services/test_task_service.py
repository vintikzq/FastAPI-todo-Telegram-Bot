import httpx
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_count, has_next",
    [
        pytest.param(6, True, id="should_show_five_tasks_and_has_next_meta_true"),
        pytest.param(1, False, id="should_show_one_task_and_has_next_meta_false"),
    ],
)
async def test_task_service_get_tasks_has_next(
    request_url, task_data, task_count, has_next, task_service, current_user, session
):
    request = httpx.Request("GET", request_url)
    tasks = [task_data for _ in range(task_count)]
    response = httpx.Response(status_code=200, json=tasks, request=request)
    session.request.return_value = response

    data = await task_service.get_tasks(current_user.id)

    assert len(data[0]) == min(task_count, 5)
    assert data[1] == has_next
