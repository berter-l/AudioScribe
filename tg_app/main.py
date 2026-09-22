import asyncio

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from config.conf import settings

TG_BOT_TOKEN = settings.tg_bot_config.api_key

async_session = AiohttpSession(proxy="")

bot = Bot(token=TG_BOT_TOKEN)

dp = Dispatcher()


@dp.message(F.audio)
async def upload_audio_file(message: Message):
    audio_file = await bot.download(message.audio)

    request_data = aiohttp.FormData()

    request_data.add_field(
        "audio", audio_file, filename="audio_file", content_type="audio/mp4"
    )

    async with aiohttp.request(
        "POST", "http://orchestrator_app:8000/audio", data=request_data
    ) as response:
        await response.text()


@dp.message(Command("start"))
async def check_connection(message: Message):
    await message.answer("hello world")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
