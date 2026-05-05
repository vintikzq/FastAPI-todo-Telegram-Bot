import logging

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, session: httpx.AsyncClient) -> None:
        self.base_url = settings.BASE_API_URL
        self.session = session

    async def _make_request(self, method: str, endpoint: str, is_form: bool = False, headers: dict | None = None, data: dict | None = None, params: dict | None = None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            if is_form:
                response = await self.session.request(method, url, headers=headers, data=data, params=params)
            else:
                response = await self.session.request(method, url, headers=headers, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Connection Error {e.response.status_code} - {e.response.text}")
            raise e
        except httpx.ConnectError as e:
            logger.error(
                "Connection Error")
            raise e
