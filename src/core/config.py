from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_HOST: str
    INTERNAL_BOT_SECRET: str
    TOKEN_TTL_SEC: int
    REDIS_HOST: str

    @property
    def BASE_API_URL(self) -> str:
        return f"http://{self.API_HOST}:8000/api/v1/"
    model_config = SettingsConfigDict(env_file='.env')

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:6379/0"


settings = Settings()  # type: ignore
