from pydantic import BaseModel


class WhisperConfig(BaseModel):
    model_name: str = "small"
    number_of_threads: int = 8
    device_type: str = "cpu"
    compute_type: str = "int8"
