from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types

def get_registered_kb() -> ReplyKeyboardMarkup:
    """
    Основное меню пользователя
    """
    markup = ReplyKeyboardBuilder()
    markup.add(KeyboardButton(text = 'Записаться на процедуру'))
    markup.add(KeyboardButton(text = 'Завершить работу'))
    return markup.as_markup(resize_keyboard=True)
