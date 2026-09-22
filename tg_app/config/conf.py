from pydantic_settings import BaseSettings

from config.tg_bot_conf import TgBotConfig


class Settings(BaseSettings):
    tg_bot_config: TgBotConfig = TgBotConfig()


settings = Settings()
