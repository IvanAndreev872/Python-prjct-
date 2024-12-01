from aiogram import Bot, Dispatcher, html, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.enums import ParseMode

import app.keybords as keys

router = Router()

"""
хэндлер начала работы, принимает на вход "/start"
"""

@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Здравствуйте!", reply_markup=keys.main)
