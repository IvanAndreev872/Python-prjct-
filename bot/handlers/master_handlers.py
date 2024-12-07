from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Appointment, Master, User
from bot.keyboards.inline_keyboards import get_master_appointments_keyboard

router = Router()

@router.message(Command("my_appointments"))
async def handle_my_appointments(message: Message, session: AsyncSession):
    """
    Обработчик команды для мастеров. Показывает записи мастера.
    """
    telegram_id = message.from_user.id

    """
    Проверяем, является ли пользователь мастером
    """
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user or user.role != "master":
        await message.answer("Команда доступна только для мастеров.")
        return

    """
    Получаем информацию о мастере
    """
    result = await session.execute(select(Master).where(Master.user_id == user.user_id))
    master = result.scalar_one_or_none()
    if not master:
        await message.answer("Вы не зарегистрированы как мастер.")
        return

    """
    Получаем записи мастера
    """
    appointments_result = await session.execute(
        select(Appointment).where(Appointment.master_id == master.master_id)
    )
    appointments = appointments_result.scalars().all()

    if appointments:
        for appointment in appointments:
            await message.answer(
                f"Запись: {appointment.start_time.strftime('%d.%m.%Y %H:%M')} - "
                f"{appointment.end_time.strftime('%H:%M')}\n"
                f"Клиент: {appointment.user.name}\n"
                f"Услуга: {appointment.service_id}\n"
                f"Статус: {appointment.status}",
                reply_markup=get_master_appointments_keyboard(appointment.appointment_id)
            )
    else:
        await message.answer("У вас нет предстоящих записей.")

@router.callback_query(lambda call: call.data.startswith("notify_"))
async def notify_client(call: CallbackQuery, session: AsyncSession):
    """
    Уведомить клиента о записи.
    """
    appointment_id = int(call.data.split("_")[1])
    result = await session.execute(
        select(Appointment).where(Appointment.appointment_id == appointment_id)
    )
    appointment = result.scalar_one_or_none()

    if appointment:
        """
        Логика отправки уведомления клиенту
        """
        await call.message.answer(
            f"Клиент {appointment.user.name} уведомлён о записи "
            f"на {appointment.start_time.strftime('%d.%m.%Y %H:%M')}."
        )
    else:
        await call.message.answer("Запись не найдена.")

@router.callback_query(lambda call: call.data.startswith("edit_"))
async def edit_appointment(call: CallbackQuery):
    """
    Логика изменения записи.
    """
    appointment_id = int(call.data.split("_")[1])
    await call.message.answer(
        f"Функция изменения записи с ID {appointment_id} пока в разработке."
    )
