import datetime
from aiogram import Bot
from bot.keyboards.inline_keyboards import get_confirmation_keyboard
from bot.database.models import SessionLocal, Notification

def make_notification(appointment, notification_type: str, send_at: int):
    """
    type: "reminder" or "confirmation"
    send_at - за сколько часов до записи.
    """
    send_time = appointment.start_time - datetime.timedelta(hours=send_at)

    with SessionLocal() as session:
        notif = Notification(
            appointment_id=appointment.appointment_id,
            notification_type=notification_type,
            send_at=send_time
        )
        session.add(notif)
        session.commit()

    return send_time

async def send_notification(bot: Bot, appointment, notification_type: str, send_at: int):
    send_time = make_notification(appointment, notification_type, send_at)
    
    user_id = appointment.user_id
    text = f"Напоминание: у вас запись {appointment.start_time}. Подтвердите или отмените."
    keyboard = get_confirmation_keyboard(appointment.appointment_id)
    await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)

    with SessionLocal() as session:
        notification = session.query(Notification).filter_by(appointment_id=appointment.appointment_id, notification_type=notification_type).first()
        if notification:
            notification.status = "sent"
            session.commit()
