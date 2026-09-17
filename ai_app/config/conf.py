from pydantic_settings import BaseSettings

from config.celery_consumer_conf import RabbitMQConfig
from config.whisper_ai_conf import WhisperConfig


class Settings(BaseSettings):
    whisper_config: WhisperConfig = WhisperConfig()
    rabbitmq_config: RabbitMQConfig = RabbitMQConfig()


settings = Settings()
