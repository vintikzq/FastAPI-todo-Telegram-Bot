import logging

import httpx

from src.core.config import settings
from src.storage.tokens import TokenStorage

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, session: httpx.AsyncClient, token_storage: TokenStorage) -> None:
        self.base_url = settings.BASE_API_URL
        self.session = session
        self.token_storage = token_storage

    async def _make_request(self, method: str, endpoint: str, user_id: int | None = None, is_form: bool = False,
                            headers: dict | None = None, data: dict | None = None,
                            params: dict | None = None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            if is_form:
                response = await self.session.request(method, url, headers=headers, data=data, params=params)
            else:
                response = await self.session.request(method, url, headers=headers, json=data, params=params)
            response.raise_for_status()

            if response.status_code == 204:
                return {}
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401 and user_id is not None:
                await self.token_storage.delete_token(user_id)
            logger.error(
                f"API Error {e.response.status_code} - {e.response.text}")
            raise e
        except httpx.ConnectError as e:
            logger.error(
                "Connection Error")
            raise e
