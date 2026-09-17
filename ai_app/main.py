from celery import Celery
from faster_whisper import WhisperModel
from config.conf import settings
from io import BytesIO

MODEL_NAME = settings.whisper_config.model_name

MODEL_DEVICE_TYPE = settings.whisper_config.device_type

MODEL_NUMBER_OF_THREADS = settings.whisper_config.number_of_threads


model = WhisperModel(
    model_size_or_path=MODEL_NAME,
    cpu_threads=MODEL_NUMBER_OF_THREADS,
    device=MODEL_DEVICE_TYPE,
    compute_type=settings.whisper_config.compute_type,
)

celery_app = Celery(broker=settings.rabbitmq_config.get_broker_url)


@celery_app.task
def get_audio_file_transcription(audio_file: BytesIO):

    raw_text = model.transcribe(audio_file)

    return raw_text
