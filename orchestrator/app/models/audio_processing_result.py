from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AudioProcessingResult(Base):
    __tablename__ = "audio_processing_result"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    result_s3_url: Mapped[str] = mapped_column(unique=True)
