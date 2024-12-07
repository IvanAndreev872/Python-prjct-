import datetime

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types
from database import models
import typing

from database.db_utils import get_service_by_appointment


def get_appointments_kb(appointments: typing.List[models.Appointment]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for appointment in appointments:
        if appointment.status != 'cancelled':
            title=f"{get_service_by_appointment(appointment).name} - {appointment.start_time.strftime('%Y:%M:%D')}"
            builder.row(types.InlineKeyboardButton(text=title, callback_data=str(appointment.appointment_id)))
    #builder.row(types.InlineKeyboardButton(text="Главное меню", callback_data='main_menu'))
    return builder.as_markup(resize_keyboard=True)

def get_conf_cancel_kb(appointment: models.Appointment) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if appointment.start_time + datetime.timedelta(hours=3) >= datetime.datetime.now() and appointment.status == 'pending':
        builder.add(types.InlineKeyboardButton(text="Подтвердить", callback_data=f'confirm_{appointment.appointment_id}'))
    if appointment.status == 'pending':
        builder.add(types.InlineKeyboardButton(text="Отменить", callback_data=f'cancel_{appointment.appointment_id}'))
    builder.add(types.InlineKeyboardButton(text="Назад", callback_data='back'))
    return builder.as_markup(resize_keyboard=True)
