from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from database import db_utils


def get_welcome_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Регистрация'))
    builder.add(types.KeyboardButton(text = 'Завершить работу'))
    return builder.as_markup(resize_keyboard=True)