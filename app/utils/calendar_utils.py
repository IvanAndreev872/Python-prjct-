import urllib.parse

from database import models


def create_event(master: models.Master, service: models.Service,
                 schedule: models.Schedule):
    return {
        'summary': 'Запись в салон красоты "Ножки в ручки"',
        'location': 'Москва, Красная площадь:))',
        'description': f'Запись на услугу: {service.name}\n'
                       f'Мастер: {master.user.name}',
        'start': schedule.start_time,
        'end': schedule.end_time,
        'timezone': 'Europe/Moscow',
    }


def create_google_calendar_link(master: models.Master, service: models.Service,
                                schedule: models.Schedule):
    event = create_event(master, service, schedule)

    base_url = 'https://www.google.com/calendar/render?action=TEMPLATE'
    params = {
        'text': event['summary'],
        'details': event['description'],
        'location': event['location'],
        'dates': f"{event['start']}/{event['end']}",
        'ctz': event['timezone']
    }
    query_string = urllib.parse.urlencode(params)

    return f"{base_url}&{query_string}"


def create_ics_file(master: models.Master, service: models.Service,
                    schedule: models.Schedule):
    event = create_event(master, service, schedule)

    ics_content = f"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:Ножки в ручки
BEGIN:VEVENT
SUMMARY:{event['summary']}
LOCATION:{event['location']}
DESCRIPTION:{event['description']}
DTSTART:{event['start']}
DTEND:{event['end']}
BEGIN:VALARM
TRIGGER:-PT30M
DESCRIPTION:Напоминание о событии
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR
    """

    with open(f"event-{schedule.schedule_id}.isc", "w", encoding="utf-8") as file:
        file.write(ics_content)


'''
Чтобы отправить файл через бота:

    with open(f"event-{schedule.schedule_id}.isc", "rb") as file:
        update.message.reply_document(document=file, filename="event.ics")
    os.remove(f"event-{schedule.schedule_id}.isc")
'''