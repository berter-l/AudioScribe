from pydantic import BaseModel, ConfigDict


class FileMetadataSchema(BaseModel):
    id: int
    name: str
    result_s3_url: str

    model_config = ConfigDict(from_attributes=True)
