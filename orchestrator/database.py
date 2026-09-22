from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config.conf import settings

DB_URL = settings.db_config.get_db_url

async_engine = create_async_engine(url=DB_URL)

async_session = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass
