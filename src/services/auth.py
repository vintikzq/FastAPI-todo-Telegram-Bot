import logging

import httpx

from src.services.base import BaseClient
from src.core.config import settings
from src.storage.tokens import TokenStorage

logger = logging.getLogger(__name__)


class AuthService(BaseClient):
    async def login_user(self, login: str, password: str):
        return await self._make_request('post', '/login', is_form=True, data={'username': login, 'password': password})

    async def create_user(self, login: str, password: str):
        return await self._make_request('post', '/register', data={'login': login, 'password': password})

    async def resolve_user(self, user_id: int):
        return await self._make_request('post', '/login/telegram', data={'telegram_id': user_id}, headers={'X-Internal-Secret': settings.INTERNAL_BOT_SECRET})

    async def get_auth_token(self, user_id: int, token_storage: TokenStorage):
        token = await token_storage.get_token(user_id)
        if token:
            return token
        try:
            response = await self.resolve_user(user_id)
            token = response.get('access_token')
            if token:
                await token_storage.save_token(user_id, token)
                return token
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error(
                    f"Login throw telegram error, invalid secret:{e.response.text}")
            else:
                logger.error(
                    f"Login throw telegram error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            return None
