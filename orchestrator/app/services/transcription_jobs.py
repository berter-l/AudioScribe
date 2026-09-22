import uuid
from io import BytesIO
from boto3.s3.transfer import TransferConfig
from app.config.conf import settings
from app.services import (
    session,
    ENDPOINT_URL,
    REGION_NAME,
    BUCKET_NAME,
    producer_celery_app,
)

DOMAIN_BUCKET_NAME = settings.s3_config.domain_bucket_name


async def upload_file_to_s3(file_path: str, audio: BytesIO):
    async with session.client(
        "s3", endpoint_url=ENDPOINT_URL, region_name=REGION_NAME
    ) as s3_client:

        await s3_client.upload_fileobj(
            audio,
            BUCKET_NAME,
            file_path,
            ExtraArgs={"ContentDisposition": "attachment"},
        )

    return file_path


async def build_file_url(file_path: str):
    return f"https://{DOMAIN_BUCKET_NAME}.s3.cloud.ru/{file_path}"


async def build_file_path():
    file_id = str(uuid.uuid4())
    return f"{file_id}"


async def save_audio_to_s3(audio: BytesIO):
    file_path = await build_file_path()

    file_url = await build_file_url(file_path)

    await upload_file_to_s3(file_path, audio)

    return file_path


async def send_transcription_jobs(audio: BytesIO, audio_name: str):
    audio_file_path = await save_audio_to_s3(audio)

    producer_celery_app.send_task(
        name="audio_transcription",
        kwargs={"audio_file_path": audio_file_path, "audio_name": audio_name},
    )
