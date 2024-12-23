from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from database.models import SessionLocal, Appointment
from aiogram import Bot
from datetime import timedelta


scheduler = AsyncIOScheduler()


async def send_reminder(chat_id: int, appointment: dict):
    """
    Отправляет напоминание клиенту.
    """
    message = (
        f"Напоминание: У вас запись на услугу '{appointment['service']}' "
        f"{appointment['date']} в {appointment['time']}.\n"
        f"Мастер: {appointment['master_name']}."
    )
    await Bot.send_message(chat_id=chat_id, text=message)


def schedule_reminders():
    """
    Планирует напоминания для всех записей.
    """
    with SessionLocal() as session:
        appointments = session.query(Appointment).all()
        for appt in appointments:
            # Запланировать напоминание за 1 день
            reminder_time_1d = appt.date - timedelta(days=1)
            scheduler.add_job(
                send_reminder,
                trigger=DateTrigger(run_date=reminder_time_1d),
                kwargs={
                    "chat_id": appt.client_id,
                    "appointment": {
                        "service": appt.service_name,
                        "date": appt.date,
                        "time": appt.time,
                        "master_name": appt.master_name,
                    },
                },
            )

            # Запланировать напоминание за 1 час
            reminder_time_1h = appt.date - timedelta(hours=1)
            scheduler.add_job(
                send_reminder,
                trigger=DateTrigger(run_date=reminder_time_1h),
                kwargs={
                    "chat_id": appt.client_id,
                    "appointment": {
                        "service": appt.service_name,
                        "date": appt.date,
                        "time": appt.time,
                        "master_name": appt.master_name,
                    },
                },
            )


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.start()
