import aioboto3
from boto3.s3.transfer import TransferConfig
from celery import Celery

from app.config.conf import settings

AWS_SECRET_ACCESS_KEY = settings.s3_config.aws_secret_access_key

TENANT_ID = settings.s3_config.tenant_id

REGION_NAME = settings.s3_config.region_name

ENDPOINT_URL = settings.s3_config.endpoint_url

BUCKET_NAME = settings.s3_config.bucket_name

AWS_ACCESS_KEY_ID = settings.s3_config.aws_access_key_id

BROKER_URL = settings.rabbitmq_config.get_url


session = aioboto3.Session(
    aws_access_key_id=f"{TENANT_ID}:{AWS_ACCESS_KEY_ID}",
    aws_secret_access_key=f"{AWS_SECRET_ACCESS_KEY}",
)

s3_transfer_config = TransferConfig(
    multipart_threshold=1 * 1024 * 1024,
    multipart_chunksize=300 * 1024,
    max_concurrency=20,
)


producer_celery_app = Celery(broker=BROKER_URL)
