from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from database import db_utils


def get_welcome_kb(user_id) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    if db_utils.check_new_user(user_id):
        builder.add(types.KeyboardButton(text='Регистрация'))
    builder.row(
        types.KeyboardButton(text='Вход'),
        types.KeyboardButton(text='Выход')
    )
    return builder.as_markup(resize_keyboard=True)