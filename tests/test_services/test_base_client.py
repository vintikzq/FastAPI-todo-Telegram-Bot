import httpx
import pytest

from src.core.exceptions import (
    AppBaseException,
    BackendServerError,
    NetworkConnectionError,
    ResourceNotFoundError,
    ValidationError,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, expected_exception",
    [
        pytest.param(
            404, ResourceNotFoundError, id="throw_404_should_catch_with_resource_not_found_error"
        ),
        pytest.param(
            500, BackendServerError, id="throw_500_should_catch_with_backend_server_error"
        ),
        pytest.param(422, ValidationError, id="throw_422_should_catch_with_validation_error"),
    ],
)
async def test_base_client_should_correctly_catch_error(
    status_code, expected_exception, session, request_url, task_service
):
    request = httpx.Request("GET", request_url)

    response = httpx.Response(status_code=status_code, request=request)

    exception = httpx.HTTPStatusError("Some error", request=request, response=response)
    session.request.side_effect = exception

    with pytest.raises(expected_exception):
        await task_service.get_task_by_id(user_id=999, task_id=1)


@pytest.mark.asyncio
async def test_base_client_token_validation_should_delete_token_on_401(
    session, storage, request_url, task_service
):
    request = httpx.Request("GET", request_url)

    status_code = 401
    response = httpx.Response(status_code=status_code, request=request)

    exception = httpx.HTTPStatusError("Some error", request=request, response=response)
    session.request.side_effect = exception

    with pytest.raises(AppBaseException):
        await task_service.get_task_by_id(user_id=999, task_id=1)

    storage.delete_token.assert_called_once()


@pytest.mark.asyncio
async def test_base_client_should_raise_network_error_on_connect_error(session, task_service):
    session.request.side_effect = httpx.ConnectError("Some error")

    with pytest.raises(NetworkConnectionError):
        await task_service.get_task_by_id(user_id=999, task_id=1)
