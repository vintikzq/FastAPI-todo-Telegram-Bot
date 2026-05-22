from src.services.base import BaseClient
from src.core.config import settings


class AuthService(BaseClient):
    """
    Silent Server-to-Server (S2S) authentication component.

    Manages the lifecycle of session JWT tokens and coordinates Redis cache warming.
    """

    async def resolve_user(self, user_id: int):
        return await self._make_request('post', '/login/telegram', data={'telegram_id': user_id}, headers={'X-Internal-Secret': settings.INTERNAL_BOT_SECRET})

    async def get_auth_token(self, user_id: int):
        token = await self.token_storage.get_token(user_id)
        if token:
            return token
        response = await self.resolve_user(user_id)
        token = response.get('access_token')
        if token:
            await self.token_storage.save_token(user_id, token)
            return token
