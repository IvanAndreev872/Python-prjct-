from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def get_registered_kb() -> ReplyKeyboardMarkup:
    """
    Основное меню пользователя
    """
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Мои записи'))
    builder.add(types.KeyboardButton(text = 'Записаться на процедуру'))
    builder.add(types.KeyboardButton(text = 'Завершить работу'))
    return builder.as_markup(resize_keyboard=True)
