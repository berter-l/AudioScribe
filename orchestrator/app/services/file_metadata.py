from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audio_processing_result import AudioProcessingResult
from app.schemes.file_metadata import FileMetadataSchema


async def get_files_metadata(session: AsyncSession):
    files_metadata_query = select(AudioProcessingResult)

    raw_files_metadata = await session.scalars(files_metadata_query)

    raw_files_metadata = raw_files_metadata.all()

    if not raw_files_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    processed_files_metadata = [
        FileMetadataSchema.model_validate(file_metadata)
        for file_metadata in raw_files_metadata
    ]

    return processed_files_metadata
