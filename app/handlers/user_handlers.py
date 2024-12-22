from aiogram import Router, F
from aiogram import types
from bot.database.models import SessionLocal, Appointment

router = Router()

@router.message(F.text.lower().strip() == 'подтвердить')
async def callback_confirm(callback_query: types.CallbackQuery):
    appointment_id = int(callback_query.data.split('_')[1])
    with SessionLocal() as session:
        appointment = session.query(Appointment).get(appointment_id)
        if appointment:
            confirm_appointment(appointment)
            await callback_query.bot.send_message(
                chat_id=appointment.user_id,
                text="Вы подтвердили запись. Мы напомним вам за час до встречи."
            )
            make_notification(appointment, "confirmation", send_at=1)

@router.message(F.text.lower().strip() == 'отменить')
async def callback_cancel(callback_query: types.CallbackQuery):
    appointment_id = int(callback_query.data.split('_')[1])
    with SessionLocal() as session:
        appointment = session.query(Appointment).get(appointment_id)
        if appointment:
            session.delete(appointment)
            session.commit()
            await callback_query.bot.send_message(
                chat_id=appointment.master_id,
                text=f"Запись клиента на {appointment.start_time} была отменена."
            )
            await callback_query.bot.send_message(
                chat_id=appointment.user_id,
                text="Вы отменили запись."
            )
