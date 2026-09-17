from fastapi import APIRouter, UploadFile

router = APIRouter()


@router.post("/audio", tags=["audio"])
async def save_transcript_text(audio: UploadFile):
    pass
