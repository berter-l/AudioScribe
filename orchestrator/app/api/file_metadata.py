from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.file_metadata import (
    get_files_metadata as service_get_files_metadata,
)
from app.dependencies import get_async_session
from app.schemes.file_metadata import FileMetadataSchema

router = APIRouter()


@router.get("/files-metadata", tags=["File Metadata"])
async def get_files_metadata(
    session: AsyncSession = Depends(get_async_session),
) -> list[FileMetadataSchema]:

    files_metadata = await service_get_files_metadata(session)

    return files_metadata
