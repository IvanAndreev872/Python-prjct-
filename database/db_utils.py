import re

from database import models
import datetime
from database.models import SessionLocal, User, Schedule, Appointment
import sqlalchemy as sa
from bot.handlers.scheduler import schedule_reminders

def check_new_user(telegram_id: int) -> bool:
    """
    Проверяет есть ли в базе такой пользователь
    """
    with models.SessionLocal() as session:
        return session.query(models.User).filter(models.User.telegram_id == telegram_id).first() is None


def add_new_user(telegram_id: int, name: str, phone: str, email: str, role='client'):
    """
    Добавляет в базу пользователя. Если телефон или почта неверные, то делает их None.
    Если пользователь с таким id уже есть, то вернет None, иначе вернет объект добавленного пользователя.
    Возможные роли: client, master, admin
    """
    if not check_new_user(telegram_id):
        return None
    if not re.match(models.PHONE_REGEX, phone):
        phone = None
    if not re.match(models.EMAIL_REGEX, email):
        email = None
    with models.SessionLocal() as session:
        user = models.User(telegram_id=telegram_id, name=name, phone=phone, email=email, role=role)
        session.add(user)
        session.commit()
        return user



def get_master_schedule(master_id: int):
    """
    Получение расписания мастера из базы данных.
    """
    with SessionLocal() as session:
        schedules = session.query(Schedule).filter(Schedule.master_id == master_id).all()
        if not schedules:
            return {}
        return {schedule.day: schedule.hours for schedule in schedules}


def get_appointments(master_id: int):
    """
    Получение записей мастера из базы данных.
    """
    with SessionLocal() as session:
        appointments = session.query(Appointment).filter(Appointment.master_id == master_id).all()
        return [
            {
                "id": appt.id,
                "date": appt.date,
                "time": appt.time,
                "client_name": appt.client_name,
                "service": appt.service_name
            }
            for appt in appointments
        ]

def get_appointment_by_id(appointment_id):
    """
    Возвращает запись по ID.
    """
    with SessionLocal() as session:
        appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return None
        return {
            "id": appointment.id,
            "client_id": appointment.user_id,
            "date": appointment.start_time.strftime("%Y-%m-%d"),
            "time": appointment.start_time.strftime("%H:%M"),
            "service": appointment.service_name,
            "master_name": appointment.master.master_name,
        }


def update_appointment_status(appointment_id: int, status: str) -> bool:
    """
    Обновление статуса записи в базе данных.
    """
    with SessionLocal() as session:
        appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not appointment:
            return False
        appointment.status = status
        session.commit()
        return True

def get_user_by_telegram_id(user_id: int):
    with SessionLocal() as session:
        result = session.execute(
            sa.select(User).where(User.telegram_id == user_id)
        )
        return result.scalar_one_or_none()


def add_new_service(name: str, description: str, price: int, duration_minutes: int):
    """
    Добавляет новую услугу в базу данных услуг, если такой еще нет.
    """
    with models.SessionLocal() as session:
        if session.query(models.Service).filter(models.Service.name == name and models.Service.duration_minutes == duration_minutes).first() is None:
            service = models.Service(name=name, description=description, price=price,
                                     duration_minutes=duration_minutes)
            session.add(service)
            session.commit()

def add_service_to_master(master: models.Master, service: str):
    """
    Внутренняя функция, которая добавляет услугу в список мастера, и мастера в список услуги
    """
    with models.SessionLocal() as session:
        service1 = session.query(models.Service).filter(models.Service.name == service).first()
        if service1 is None:
            raise ValueError(f"Услуги {service} нет в базе данных услуг. Добавьте сначала туда.")
        master.specializations.append(service1)
        session.commit()

def add_new_master(telegram_id: int, experience_years: int, services: list[str]):
    """
    Предполагаю, что мастер перед тем как стать мастером сначала взаимодествует с ботом, то есть он уже есть в БД как user.
    (Например нажимает кнопку стать мастером и пишет некоторый код, который получает от админа после собеса)
    Добавляет нового мастера, в списке services должны быть написаны названия услуг, которые УЖЕ лежат в БД услуг.
    Если там чего-то нет, то нужно сначала вызвать для них функцию add_new_service.
    (Предполагаю, что добавлять новое может только админ) А мастер только выбирает из существующего списка кнопками.
    """
    if check_new_user(telegram_id):
        raise ValueError("Такого пользователя нет в БД, сначала должен появится там!")
    with models.SessionLocal() as session:
        user = session.query(models.User).filter(models.User.telegram_id == telegram_id).first()
        if user.role == 'master':
            return
        user.role = 'master'
        master = models.Master(user_id=user.user_id, experience_years=experience_years)
        for service in services:
            add_service_to_master(master, service)

        session.add(master)
        session.commit()

def add_master_code(code: str, description: str, user_id: int = None):
    """
    Добавляет новый код мастера в базу данных, если такого кода ещё нет.
    """
    with models.SessionLocal() as session:
        existing_code = session.query(models.MasterCode).filter_by(code=code).first()
        if existing_code:
            print(f"Код '{code}' уже существует в базе данных.")
            return

        master_code = models.MasterCode(code=code, description=description, user_id=user_id)
        session.add(master_code)
        session.commit()
        print(f"Код '{code}' успешно добавлен.")

def get_master_code(code: str):
    """
    Возвращает мастер-код из базы данных.
    """
    with models.SessionLocal() as session:
        master_code = session.query(models.MasterCode).filter_by(code=code).first()
        return master_code


def assign_master_code_to_user(user_id: int, code: str):
    """
    Сопоставляет пользователя с кодом мастера.
    """
    with models.SessionLocal() as session:
        user = session.query(models.User).filter_by(user_id=user_id).first()
        if not user:
            raise ValueError("Пользователь не найден.")

        master_code = session.query(models.MasterCode).filter_by(code=code).first()
        if not master_code:
            raise ValueError("Код мастера не найден.")

        if master_code.user_id:
            raise ValueError("Этот код уже использован другим пользователем.")

        # Сопоставляем код с пользователем
        master_code.user_id = user.user_id
        session.commit()


def is_user_linked_to_code(user_id: int, code: str) -> bool:
    """
    Проверяет, связан ли пользователь с кодом мастера.
    """
    with models.SessionLocal() as session:
        master_code = session.query(models.MasterCode).filter_by(code=code, user_id=user_id).first()
        return master_code is not None

def get_master_code_by_user_id(user_id: int) -> str | None:
    """
    Получает код мастера для конкретного пользователя.
    """
    with models.SessionLocal() as session:
        master_code = session.query(models.MasterCode).filter_by(user_id=user_id).first()
        return master_code.code if master_code else None

def get_services_by_master(master: models.Master):
    """
    Получить услуги, которые предоставляет мастер
    """
    return list(master.specializations)

def get_masters_by_service(service1: models.Service):
    return list(service1.masters)

def add_new_schedule_to_master(master: models.Master, start_time, end_time):
    """
    Время начала и конца должно быть кратно 30 минутам!
    Добавляет новый промежуток рабочего времени для мастера, если этот промежуток пересекается с уже существующим,
    то в базе будет храниться их объединение
    """
    lst = []
    begin = start_time
    end = start_time + datetime.timedelta(minutes=30)
    while end <= end_time:
        schedule_tmp = models.Schedule(master_id=master.master_id, start_time=begin, end_time=end)
        lst.append(schedule_tmp)
        begin += datetime.timedelta(minutes=30)
        end += datetime.timedelta(minutes=30)

    with models.SessionLocal() as session:
        masters_schedule = master.schedule
        for sch in lst:
            flag = True
            for sch2 in masters_schedule:
                if sch2.start_time == sch.start_time:
                    flag = False
                    break
            if flag:
                session.add(sch)

        session.commit()

def get_schedules_by_master(master: models.Master):
    """
    В БД хранятся равные промежутки по 30 минут (у каждого время начала кратно 30 минутам)
    """
    return master.schedule

def get_master_by_schedule(schedule: models.Schedule):
    return schedule.master

def get_schedules_by_service_and_master(master: models.Master, service: models.Service)->list[models.Schedule]:
    """
    Выдает допустимые промежутки для записи по данной услуге и мастеру.
    """
    res = []
    free_schedules = []
    for schedule in get_schedules_by_master(master):
        flag = True
        for appoint in master.appointments:
            if (appoint.status in ['pending', 'confirmed']) and (appoint.start_time <= schedule.start_time < appoint.end_time or schedule.start_time < datetime.datetime.now()):
                flag = False
        if flag:
            free_schedules.append(schedule)

    free_schedules.sort(key=lambda x: x.start_time)
    begin_i = 0
    while begin_i < len(free_schedules):
        cur_i = begin_i + 1
        cur_time = 30
        while cur_i < len(free_schedules) and free_schedules[cur_i].start_time == free_schedules[cur_i - 1].end_time:
            cur_i += 1
            cur_time += 30
        if cur_time >= service.duration_minutes:
            res.append(free_schedules[begin_i])

        begin_i += 1
    return res

def get_schedules_by_service(service: models.Service) -> dict[models.Master, list[models.Schedule]]:
    """
    Возвращает словарь Мастер - список промежутков времени, на которые возможна запись
    """
    res = {}
    with models.SessionLocal() as session:
        for master in session.query(models.Master):
            res[master] = get_schedules_by_service_and_master(master, service)
    return res

def add_new_appointment(master: models.Master, user: models.User, service: models.Service, schedule: models.Schedule):
    """
    Делает новую запись, на дотупное время. Этот schedule должен быть получен при помощи 1 из 2х функций сверху.
    """
    with models.SessionLocal() as session:
        app = models.Appointment(user_id = user.user_id, master_id=master.master_id, service_id=service.service_id,
                                 start_time=schedule.start_time, end_time=schedule.start_time + datetime.timedelta(minutes=service.duration_minutes))
        session.add(app)
        session.commit()

    schedule_reminders()
def cancel_appointment(appointment: models.Appointment):
    with models.SessionLocal() as session:
        appointment.status = 'cancelled'
        session.commit()

def confirm_appointment(appointment: models.Appointment):
    with models.SessionLocal() as session:
        appointment.status = 'confirmed'
        session.commit()

def make_notification(appointment: models.Appointment, type: str, send_at: int):
    """
    type: "reminder" or "confirmation"
    send_at - за сколько часов до записи.
    """
    with models.SessionLocal() as session:
        notif = models.Notification(appointment_id = appointment.appointment_id, notification_type = type,
                                    send_at = appointment.start_time - datetime.timedelta(hours=send_at))
        session.add(notif)
        session.commit()

def delete_master(master: models.Master):
    """
    Все эти функции удаления должны каскадом удалять все связанные записи.
    """
    with models.SessionLocal() as session:
        session.delete(master)
        session.commit()

def delete_user(user: models.User):
    with models.SessionLocal() as session:
        session.delete(user)
        session.commit()

def delete_service(service: models.Service):
    with models.SessionLocal() as session:
        session.delete(service)
        session.commit()
