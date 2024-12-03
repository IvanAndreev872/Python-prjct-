from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def get_registered_kb() -> ReplyKeyboardMarkup:
    """
    Сюда добавлять кнопки после авторизации/регистрации
    """
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Мои записи'))
    return builder.as_markup(resize_keyboard=True)