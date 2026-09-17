from fastapi import APIRouter

router = APIRouter()


@router.post("/internal/transcription-results", tags=["transcription"])
async def save_transcription_result(transcription_result: str):
    pass
