from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

from database import models

async def get_masterts() -> InlineKeyboardMarkup :
    markup = InlineKeyboardBuilder()
    for master in models.Master() :
        markup.add(InlineKeyboardButton(text=master.name, callback_data=f'мастер {master.name}'))
    return markup.as_markup(resize_keyboard=True)

async def get_service() -> InlineKeyboardMarkup :
    markup = InlineKeyboardBuilder()
    for service in models.Service() :
        markup.add(InlineKeyboardButton(service.name, callback_data=f'услуга {service.name}'))
    return markup.as_markup(resize_keyboard=True)
