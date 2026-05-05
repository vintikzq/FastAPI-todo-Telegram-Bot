import logging

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


class BaseClient:
    def __init__(self, session: httpx.AsyncClient) -> None:
        self.base_url = settings.BASE_API_URL
        self.session = session

    async def _make_request(self, method: str, endpoint: str, is_form: bool = False, data: dict | None = None, params: dict | None = None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            if is_form:
                response = await self.session.request(method, url, data=data, params=params)
            else:
                response = await self.session.request(method, url, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise e
        except httpx.ConnectError as e:
            logger.error(
                f"Connection Error")
            raise e
