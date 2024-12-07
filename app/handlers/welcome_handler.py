from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.keyboards import registered_users_kb
from app.keyboards import welcome_keyboard

from database import db_utils

router = Router()

"""
хэндлер начала работы, принимает на вход "/start"
"""

@router.message(CommandStart())
async def command_start_handler(message: Message):
    """
    Выдает кнопку регистрации, только если юзера с таким ID нет в нашей БД.
    """
    if db_utils.check_new_user(message.from_user.id):
        kb = welcome_keyboard()
    else :
        kb = registered_users_kb()
    await message.answer(f"Здравствуйте!", reply_markup=kb)
