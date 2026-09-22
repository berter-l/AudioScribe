from io import BytesIO

from fastapi import APIRouter, UploadFile

from app.services.transcription_jobs import send_transcription_jobs

router = APIRouter()


@router.post("/audio", tags=["audio"])
async def save_transcript_text(audio: UploadFile):

    audio_content = await audio.read()
    audio_name = audio.filename

    await send_transcription_jobs(BytesIO(audio_content), audio_name)
