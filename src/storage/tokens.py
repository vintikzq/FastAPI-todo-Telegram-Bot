class TokenStorage():
    def __init__(self) -> None:
        self.token_storage = {}

    async def save_token(self, user_id: int, token: str):
        self.token_storage[user_id] = token

    async def get_token(self, user_id: int):
        return self.token_storage.get(user_id)

    async def delete_toke(self, user_id: int):
        del self.token_storage[user_id]
