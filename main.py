import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


import app.handlers.make_appointment
import app.handlers.welcome_handler
from config_reader import config
import app.handlers.registration
import app.handlers.my_appointments
import app.middlewares.session_control
from database.models import Base, engine
import app.handlers.make_appointment

dp = Dispatcher()


"""
самое начало нашего бота. создали его, и написали с какими серверами связываться
"""

async def main() -> None:
    Base.metadata.create_all(engine)
    dp.include_router(app.handlers.welcome_handler.router)
    dp.include_router(app.handlers.registration.router)
    dp.include_router(app.handlers.make_appointment.router)
    dp.include_router(app.handlers.my_appointments.router)
    dp.update.middleware(app.middlewares.session_control.SessionControlMiddleware())
    bot = Bot(token = config.bot_token.get_secret_value(), default = DefaultBotProperties(parse_mode = ParseMode.HTML))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print ('Exit')