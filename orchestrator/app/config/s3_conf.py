from pydantic import BaseModel


class S3Config(BaseModel):
    region_name: str = "ru-central-1"
    aws_secret_access_key: str = ""
    aws_access_key_id: str = ""
    tenant_id: str = ""
    bucket_name: str = ""
    domain_bucket_name: str = ""
    endpoint_url: str = "https://s3.cloud.ru"
