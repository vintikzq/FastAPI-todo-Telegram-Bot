import httpx

from src.core.config import settings


class BaseClient:
    def __init__(self, session: httpx.AsyncClient) -> None:
        self.base_url = settings.BASE_API_URL
        self.session = session

    async def _make_request(self, method: str, endpoint: str, data: dict | None = None, params: dict | None = None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = await self.session.request(method, url, json=data, params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPStatusError, httpx.ConnectError) as e:
            raise e
