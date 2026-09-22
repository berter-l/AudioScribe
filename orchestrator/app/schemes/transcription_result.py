from pydantic import BaseModel


class TranscriptionResultSchema(BaseModel):
    transcription_text: str
    audio_name: str
