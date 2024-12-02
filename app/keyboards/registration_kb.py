from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def get_registration_kb() -> ReplyKeyboardMarkup:
    """
    Сюда добавлять кнопки после авторизации/регистрации
    """
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Отмена'))
    return builder.as_markup(resize_keyboard=True)