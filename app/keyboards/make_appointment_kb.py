from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types

from database import models
from database.db_utils import get_all_services
from database.db_utils import get_masters_by_service
from database.db_utils import get_user_by_master
from database.db_utils import get_schedules_by_service_and_master

import typing

def cancel_appointment() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Отмена'))
    return builder.as_markup(resize_keyboard=True)

async def get_right_masterts(service1: models.Service) -> InlineKeyboardMarkup :
    masters = get_masters_by_service(service1)
    markup = InlineKeyboardBuilder()
    for master in masters :
        master_name = get_user_by_master(master).name
        markup.add(InlineKeyboardButton(master_name, callback_data=f'master id: {master.master_id}'))
    return markup.as_markup(resize_keyboard=True)

async def get_service(remover=0) -> InlineKeyboardMarkup :
    services = get_all_services()
    markup = InlineKeyboardBuilder()
    for count, service in enumerate(services) :
        if count < 10 :
            markup.add(InlineKeyboardButton(service.name, callback_data=f'service id: {service.service_id}'))
    return markup.as_markup(resize_keyboard=True)


async def get_free_windows(master: models.Master, service: models.Service) -> InlineKeyboardBuilder :
    schedule = get_schedules_by_service_and_master(master=master, service=service)
    markup = InlineKeyboardBuilder()
    for time in schedule :
        window = f'{time.start_time} - {time.end_time}'
        markup.add(InlineKeyboardButton(window, callback_data=f'window: {time.schedule_id}'))
    return markup.as_markup(resize_keyboard=True)


