from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram import types
import math

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

async def get_right_masterts(service1: models.Service, remover=0) -> InlineKeyboardMarkup :
    masters = get_masters_by_service(service1)
    markup = InlineKeyboardBuilder()
    for count, master_num in enumerate(range(remover, len(masters))) :
        if count < 10 :
            master_name = get_user_by_master(masters[master_num]).name
            markup.add(InlineKeyboardButton(text=master_name, callback_data=f'master id: {masters[master_num].master_id}'))
        else :
            break
    
    if (len(masters) <= 10) : pass
    elif (len(masters) > 10 and remover < 10) :
        markup.add(
            InlineKeyboardButton(f"1/{math.ceil(len(masters) / 10)}", callback_data="..."),
            InlineKeyboardButton ("Далее 👉", callback_data=f"swipe_masters:{remover + 10}")
        )
    elif (remover + 10 >= len(masters)):
        markup.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"swipe_masters:{remover - 10}"),
            InlineKeyboardButton(f"{str(remover + 10)[:-1]}/{math.ceil(len(masters) / 10)}", callback_data="..."), 
        )
    else:
        markup.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"swipe_masters:{remover - 10}"),
            InlineKeyboardButton(f"{str(remover + 10)[:-1]}/{math.ceil(len(masters) / 10)}", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"swipe_masters:{remover + 10}"),
        )
    return markup.as_markup(resize_keyboard=True)

async def get_service(remover=0) -> InlineKeyboardMarkup :
    services = get_all_services()
    markup = InlineKeyboardBuilder()
    for count, service_num in enumerate(range(remover, len(services))):
        if count < 10 :
            markup.add(InlineKeyboardButton(services[service_num].name, callback_data=f'service id: {services[service_num].service_id}'))
        else :
            break

    if (len(services) <= 10) : pass
    elif (len(services) > 10 and remover < 10) :
        markup.add(
            InlineKeyboardButton(f"1/{math.ceil(len(services) / 10)}", callback_data="..."),
            InlineKeyboardButton ("Далее 👉", callback_data=f"swipe_services:{remover + 10}")
        )
    elif (remover + 10 >= len(services)):
        markup.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"swipe_services:{remover - 10}"),
            InlineKeyboardButton(f"{str(remover + 10)[:-1]}/{math.ceil(len(services) / 10)}", callback_data="..."), 
        )
    else:
        markup.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"swipe_services:{remover - 10}"),
            InlineKeyboardButton(f"{str(remover + 10)[:-1]}/{math.ceil(len(services) / 10)}", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"swipe_services:{remover + 10}"),
        )   
    return markup.as_markup(resize_keyboard=True)

async def get_free_windows(master: models.Master, service: models.Service, remover=0) -> InlineKeyboardMarkup :
    schedule = get_schedules_by_service_and_master(master=master, service=service)
    markup = InlineKeyboardBuilder()
    for count, time_num in enumerate(range(remover, len(schedule))) :
        if count < 10 :
            window = f'{schedule[time_num].start_time} - {schedule[time_num].end_time}'
            markup.add(InlineKeyboardButton(text=window, callback_data=f'window: {schedule[time_num].schedule_id}'))
        else :
            break

    if (len(schedule) <= 10) : pass
    elif (len(schedule) > 10 and remover < 10) :
        markup.add(
            InlineKeyboardButton(f"1/{math.ceil(len(schedule) / 10)}", callback_data="..."),
            InlineKeyboardButton ("Далее 👉", callback_data=f"swipe_time:{remover + 10}")
        )
    elif (remover + 10 >= len(schedule)):
        markup.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"swipe_time:{remover - 10}"),
            InlineKeyboardButton(f"{str(remover + 10)[:-1]}/{math.ceil(len(schedule) / 10)}", callback_data="..."), 
        )
    else:
        markup.add(
            InlineKeyboardButton("👈 Назад", callback_data=f"swipe_time:{remover - 10}"),
            InlineKeyboardButton(f"{str(remover + 10)[:-1]}/{math.ceil(len(schedule) / 10)}", callback_data="..."),
            InlineKeyboardButton("Далее 👉", callback_data=f"swipe_time:{remover + 10}"),
        )
    return markup.as_markup(resize_keyboard=True)


