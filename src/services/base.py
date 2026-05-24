import httpx

from src.core.config import settings
from src.core.exceptions import (
    AppBaseException,
    BackendServerError,
    NetworkConnectionError,
    NotAuthorizedError,
    ResourceNotFoundError,
    ValidationError,
)
from src.storage.tokens import TokenStorage


class BaseClient:
    """
    Abstract fault-tolerant gateway for external REST API integration.

    Encapsulates global network exceptions handling, HTTP mapping,
    and automatic token cache invalidation.
    """

    def __init__(self, session: httpx.AsyncClient, token_storage: TokenStorage) -> None:
        self.base_url = settings.BASE_API_URL
        self.session = session
        self.token_storage = token_storage

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        user_id: int | None = None,
        is_form: bool = False,
        headers: dict | None = None,
        data: dict | None = None,
        params: dict | None = None,
    ):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        if user_id:
            token = await self.token_storage.get_token(user_id)
            headers = headers or {}
            headers["Authorization"] = f"Bearer {token}"

        try:
            if is_form:
                response = await self.session.request(
                    method, url, headers=headers, data=data, params=params
                )
            else:
                response = await self.session.request(
                    method, url, headers=headers, json=data, params=params
                )
            response.raise_for_status()

            if response.status_code == 204:
                return {}
            return response.json()

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            if status_code == 401 and user_id is not None:
                await self.token_storage.delete_token(user_id)

            match status_code:
                case 404:
                    raise ResourceNotFoundError()
                case 500 | 502 | 503:
                    raise BackendServerError()
                case 422:
                    raise ValidationError()
                case 403:
                    raise NotAuthorizedError()
                case _:
                    raise AppBaseException(f"Unknown API Error: {status_code}")

        except httpx.ConnectError:
            raise NetworkConnectionError()
