from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from database import db_utils

def get_admin_kb(user_id) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Статистика'))
    builder.add(types.KeyboardButton(text='Добавить админа'))
    builder.add(types.KeyboardButton(text='Удалить админа'))
    builder.row(
        types.KeyboardButton(text='Добавить мастера'),
        types.KeyboardButton(text='Удалить мастера')
    )
    return builder.as_markup(resize_keyboard=True)