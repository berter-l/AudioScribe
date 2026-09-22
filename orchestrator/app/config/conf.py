from pydantic_settings import BaseSettings

from app.config.db_conf import DataBaseConfig
from app.config.rabbitmq_conf import RabbitMQConfig
from app.config.s3_conf import S3Config


class Settings(BaseSettings):
    rabbitmq_config: RabbitMQConfig = RabbitMQConfig()
    db_config: DataBaseConfig = DataBaseConfig()
    s3_config: S3Config = S3Config()


settings = Settings()
