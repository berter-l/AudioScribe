from pydantic import BaseModel


class DataBaseConfig(BaseModel):
    port: int = 5432
    username: str = "main_db"
    password: str = "1234"
    host: str = "db"
    database_name: str = "audio_transcription"

    @property
    def get_db_url(self):
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database_name}"
