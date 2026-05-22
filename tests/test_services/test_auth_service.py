import httpx
import pytest


@pytest.mark.asyncio
async def test_auth_service_token_exist_should_get_token_and_not_touch_backend(
    auth_service, storage,
    current_user, session
):
    token = "existing_jwt_token"
    storage.get_token.return_value = token

    data = await auth_service.get_auth_token(current_user.id)

    assert data == token

    session.request.assert_not_called()


@pytest.mark.asyncio
async def test_auth_service_token_not_exist_should_resolve_token(
    auth_service, storage,
    current_user, session,
    request_url
):
    token = 'new_jwt_token'
    request = httpx.Request('GET', request_url)
    response = httpx.Response(status_code=200, json={
                              'access_token': token}, request=request)
    storage.get_token.return_value = None
    session.request.return_value = response

    assert await auth_service.get_auth_token(current_user.id) == token

    storage.save_token.assert_called_once_with(
        current_user.id, token)
