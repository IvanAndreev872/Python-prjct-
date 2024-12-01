import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import TOKEN

from app.handlers import router

dp = Dispatcher()


"""
самое начало нашего бота. создали его, и написали с какими серверами связываться
"""

async def main() -> None:
    dp.include_router(router)
    bot = Bot(token = TOKEN, default = DefaultBotProperties(parse_mode = ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print ('Exit')