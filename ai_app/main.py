import boto3
from celery import Celery
from faster_whisper import WhisperModel
from config.conf import settings
from io import BytesIO
import requests
from openai import OpenAI

MODEL_NAME = settings.whisper_config.model_name

MODEL_DEVICE_TYPE = settings.whisper_config.device_type

MODEL_NUMBER_OF_THREADS = settings.whisper_config.number_of_threads

BUCKET_NAME = settings.s3_config.bucket_name

ORCHESTRATOR_URL = "http://orchestrator_app:8000/internal/transcription-results"

REGION_NAME = settings.s3_config.region_name

ENDPOINT_URL = settings.s3_config.endpoint_url

TENANT_ID = settings.s3_config.tenant_id

KEY_ID = settings.s3_config.aws_access_key_id

model = WhisperModel(
    model_size_or_path=MODEL_NAME,
    cpu_threads=MODEL_NUMBER_OF_THREADS,
    device=MODEL_DEVICE_TYPE,
    compute_type=settings.whisper_config.compute_type,
)

consumer_celery_app = Celery(broker=settings.rabbitmq_config.get_url)

s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=f"{TENANT_ID}:{KEY_ID}",
    aws_secret_access_key=settings.s3_config.aws_secret_access_key,
    region_name=REGION_NAME,
)


@consumer_celery_app.task(name="audio_transcription")
def obtain_a_transcribed_audio_recording(audio_file_path: str, audio_name: str):
    audio_file = get_audio_file_transcription(audio_file_path)

    transcript_text = transcribe_audio(audio_file)

    requests.post(
        url=ORCHESTRATOR_URL,
        json={"transcription_text": transcript_text, "audio_name": audio_name},
    )


def transcribe_audio(audio: BytesIO) -> str:
    raw_text, info = model.transcribe(audio)

    raw_text = "".join([piece_of_text.text for piece_of_text in raw_text])

    return raw_text


def get_audio_file_transcription(audio_file_path: str) -> BytesIO:
    audio_file = BytesIO()

    s3_client.download_fileobj(BUCKET_NAME, audio_file_path, audio_file)
    audio_file.seek(0)
    return audio_file
