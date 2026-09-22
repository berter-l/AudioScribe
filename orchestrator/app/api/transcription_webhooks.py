from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_async_session
from app.schemes.transcription_result import TranscriptionResultSchema
from app.services.transcription_webhooks import handle_transcription_result

router = APIRouter()


@router.post("/internal/transcription-results", tags=["transcription"])
async def save_transcription_result(
    result_data: TranscriptionResultSchema,
    session: AsyncSession = Depends(get_async_session),
):
    await handle_transcription_result(
        result_data.transcription_text, result_data.audio_name, session
    )
