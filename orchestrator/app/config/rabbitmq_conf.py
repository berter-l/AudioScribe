from pydantic import BaseModel


class RabbitMQConfig(BaseModel):
    port: int = 5672
    host: str = "rabbitmq_query"
    username: str = "guest"
    password: str = "guest"

    @property
    def get_url(self):
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}"
