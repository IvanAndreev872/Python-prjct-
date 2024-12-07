from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
import aiogram

from app.keyboards.registered_users_kb import get_registered_kb
from app.keyboards.welcome_keyboard import get_welcome_kb

router = Router()

"""
хэндлер начала работы, принимает на вход "/start"
"""

@router.message(CommandStart())
async def command_start_handler(message: Message):
    """
    Выдает кнопку регистрации, только если юзера с таким ID нет в нашей БД.
    """
    kb = get_welcome_kb(message.from_user.id)
    await message.answer(f"Здравствуйте!", reply_markup=kb)

@router.message(aiogram.F.text == "Вход")
async def enter_handler(message: Message):
    kb = get_registered_kb()
    await message.answer(text='Главное меню', reply_markup=kb)
