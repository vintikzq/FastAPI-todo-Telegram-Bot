from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    BASE_API_URL: str = "http://localhost:8000/api/v1/"
    INTERNAL_BOT_SECRET: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings() # type: ignore
