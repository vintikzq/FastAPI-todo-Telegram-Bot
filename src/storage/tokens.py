from redis.asyncio import Redis

from src.core.config import settings


class TokenStorage():
    """
    Low-level asynchronous Redis adapter for auth session caching.

    Provides atomic CRUD operations for user JWT tokens backed by TTL enforcement.
    """

    def __init__(self, redis_client: Redis) -> None:
        self.redis_client = redis_client

    async def save_token(self, user_id: int, token: str):
        await self.redis_client.set(name=self._get_key(user_id), value=token, ex=settings.TOKEN_TTL_SEC)

    async def get_token(self, user_id: int):
        return await self.redis_client.get(self._get_key(user_id))

    async def delete_token(self, user_id: int):
        await self.redis_client.delete(self._get_key(user_id))

    async def is_authorized(self, user_id: int):
        return bool(await self.redis_client.exists(self._get_key(user_id)))

    def _get_key(self, user_id: int) -> str:
        return f"bot:user:{user_id}:token"
