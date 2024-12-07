from bot.notifications.reminders import send_notification

async def start_scheduler(bot):
    with SessionLocal() as session:
        notifications = session.query(Notification).filter(Notification.send_at <= datetime.now()).all()
        for notification in notifications:
            appointment = session.query(Appointment).get(notification.appointment_id)
            if appointment:
                await send_notification(bot, appointment)
                session.delete(notification)
        session.commit()
