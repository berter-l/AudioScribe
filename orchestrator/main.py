from contextlib import asynccontextmanager

from starlette.middleware.cors import CORSMiddleware

from app.api.transcription_jobs import router as transcription_jobs_router
from app.api.transcription_webhooks import router as transcription_webhooks_router
from app.api.file_metadata import router as file_metadata_router
import uvicorn
from fastapi import FastAPI

from database import async_engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcription_jobs_router)
app.include_router(transcription_webhooks_router)
app.include_router(file_metadata_router)

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
