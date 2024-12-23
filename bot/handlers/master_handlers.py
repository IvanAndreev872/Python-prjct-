from aiogram import Router, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db_utils

router = Router()

@router.message(F.text == "Экран мастера")
async def master_dashboard(message: types.Message):
    """
    Главный экран мастера с выбором действий.
    """
    user_id = message.from_user.id
    user = db_utils.get_user_by_telegram_id(user_id)

    if not user or user.role != "master":
        await message.answer("У вас нет доступа к экрану мастера.")
        return

    # Клавиатура для действий мастера
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить график работы", callback_data="send_schedule")],
        [InlineKeyboardButton(text="Мои записи", callback_data="view_appointments")],
        [InlineKeyboardButton(text="Отправить статистику", callback_data="send_statistics")],
    ])
    await message.answer("Добро пожаловать в экран мастера. Выберите действие:", reply_markup=keyboard)

@router.callback_query(lambda query: query.data == "view_appointments")
async def view_appointments(callback: types.CallbackQuery):
    """
    Обработчик просмотра записей мастера.
    """
    user_id = callback.from_user.id
    appointments = db_utils.get_appointments(user_id)

    if not appointments:
        await callback.message.answer("У вас пока нет записей.")
        await callback.answer()
        return

    for appt in appointments:
        text = (
            f"Дата: {appt['date']}\n"
            f"Время: {appt['time']}\n"
            f"Клиент: {appt['client_name']}\n"
            f"Услуга: {appt['service']}"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Уведомить клиента", callback_data=f"notify_{appt['id']}")],
        ])
        await callback.message.answer(text, reply_markup=keyboard)

    await callback.answer()

@router.callback_query(lambda query: query.data.startswith("notify_"))
async def notify_client(callback: types.CallbackQuery):
    """
    Уведомление клиента о записи.
    """
    appointment_id = callback.data.split("_")[1]
    appointment = db_utils.get_appointment_by_id(appointment_id)

    if not appointment:
        await callback.message.answer("Ошибка: запись не найдена.")
        await callback.answer()
        return

    # Отправка уведомления клиенту
    message = (
        f"Напоминание: У вас запись на услугу '{appointment['service']}' "
        f"{appointment['date']} в {appointment['time']}.\n"
        f"Мастер: {appointment['master_name']}."
    )
    await callback.message.bot.send_message(chat_id=appointment['client_id'], text=message)
    await callback.message.answer("Клиент уведомлен.")
    await callback.answer()
