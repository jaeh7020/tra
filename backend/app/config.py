from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TDX_CLIENT_ID: str = ""
    TDX_CLIENT_SECRET: str = ""
    SECRET_KEY: str = "change-this-secret-key"
    DATABASE_URL: str = "sqlite:///./tra.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    SCHEDULER_INTERVAL_MINUTES: int = 3
    LINE_CHANNEL_ACCESS_TOKEN: str = ""
    LINE_CHANNEL_SECRET: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
