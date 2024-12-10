import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BotBlocked, MessageCantBeDeleted, MessageToDeleteNotFound

from database import db_utils


async def send_confirmation(bot: Bot, appointment):
    if appointment:
        text = f"Напоминание: у вас запись {appointment.start_time}. Подтвердите?"
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Подтвердить", callback_data=f"confirm:{appointment.appointment_id}"),
            InlineKeyboardButton("Отменить", callback_data=f"cancel:{appointment.appointment_id}")
        )
        try:
            await bot.send_message(appointment.user_id, text, reply_markup=keyboard)
        except (BotBlocked, MessageCantBeDeleted, MessageToDeleteNotFound):
            print(f"Ошибка отправки подтверждения пользователю {appointment.user_id}")


async def send_reminder(bot: Bot, appointment, reminder_type: str):
    if appointment:
        text = f"Напоминание о {reminder_type}: у вас запись {appointment.start_time}!"
        try:
            await bot.send_message(appointment.user_id, text)
        except (BotBlocked, MessageCantBeDeleted, MessageToDeleteNotFound):
            print(f"Ошибка отправки напоминания пользователю {appointment.user_id}")


async def send_notifications_job(bot: Bot):
    appointments = await db_utils.get_appointments()
    for appointment in appointments:
        if datetime.timedelta(hours=24) >= appointment.start_time - datetime.datetime.now() > datetime.timedelta(
                hours=23):
            await send_reminder(bot, appointment, "24 часа")

        if datetime.timedelta(hours=1) >= appointment.start_time - datetime.datetime.now() > datetime.timedelta(
                hours=0):
            await send_reminder(bot, appointment, "1 час")

        if datetime.timedelta(hours=0) >= appointment.start_time - datetime.datetime.now() > datetime.timedelta(
                hours=-1):
            await send_confirmation(bot, appointment)
