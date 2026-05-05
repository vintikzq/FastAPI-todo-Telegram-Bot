from src.services.base import BaseClient


class AuthService(BaseClient):
    async def login_user(self, login: str, password: str):
        return await self._make_request('post', '/login', is_form=True, data={'username': login, 'password': password})

    async def create_user(self, login: str, password: str):
        return await self._make_request('post', 'register', data={'login': login, 'password': password})
