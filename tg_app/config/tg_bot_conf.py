from pydantic import BaseModel


class TgBotConfig(BaseModel):
    api_key: str = ""
