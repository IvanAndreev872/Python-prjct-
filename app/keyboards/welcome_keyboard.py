from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import types
from database import db_utils

def get_welcome_kb(user_id) -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с учетом роли пользователя.
    """
    builder = ReplyKeyboardBuilder()
    user = db_utils.get_user_by_telegram_id(user_id)

    if not user:
        builder.add(types.KeyboardButton(text="Регистрация"))
    else:
        if user.role == "master":
            builder.add(types.KeyboardButton(text="Экран мастера"))
        else:
            builder.add(types.KeyboardButton(text="Стать мастером"))
            builder.add(types.KeyboardButton(text="Главное меню"))

    return builder.as_markup(resize_keyboard=True)
