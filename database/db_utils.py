import re
import typing

from database import models
import datetime

current_session = None

def get_session():
    global current_session
    if current_session is None:
        current_session = models.SessionLocal()
    return current_session

def check_new_user(telegram_id: int, session = None) -> bool:
    """
    Проверяет есть ли в базе такой пользователь
    """
    if session is None:
        session = get_session()
    return session.query(models.User).filter(models.User.telegram_id == telegram_id).first() is None


def add_new_user(telegram_id: int, name: str, phone: str, email: str, role='client', session=None):
    """
    Добавляет в базу пользователя. Если телефон или почта неверные, то делает их None.
    Если пользователь с таким id уже есть, то вернет None, иначе вернет объект добавленного пользователя.
    Возможные роли: client, master, admin
    """
    session = session or get_session()
    if not check_new_user(telegram_id, session):
        return None
    if not re.match(models.PHONE_REGEX, phone):
        phone = None
    if not re.match(models.EMAIL_REGEX, email):
        email = None
    user = models.User(telegram_id=telegram_id, name=name, phone=phone, email=email, role=role)
    session.add(user)
    session.commit()
    return user

def get_user_by_telegram_id(telegram_id: int, session = None) -> models.User:
    session = session or get_session()
    user = session.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    return user

def get_user_by_master(master: models.Master, session = None) -> models.User:
    return master.user

def add_new_service(name: str, description: str, price: int, duration_minutes: int, session=None):
    """
    Добавляет новую услугу в базу данных услуг, если такой еще нет.
    """
    session = session or get_session()
    if session.query(models.Service).filter(models.Service.name == name and models.Service.duration_minutes == duration_minutes).first() is None:
        service = models.Service(name=name, description=description, price=price,
                                     duration_minutes=duration_minutes)
        session.add(service)
        session.commit()

def get_service_by_name(name: str, session = None) -> models.Service:
    session = session or get_session()
    return session.query(models.Service).filter(models.Service.name == name).first()

def add_service_to_master(master: models.Master, service: str, session=None):
    """
    Внутренняя функция, которая добавляет услугу в список мастера, и мастера в список услуги
    """
    session = session or get_session()
    service1 = session.query(models.Service).filter(models.Service.name == service).first()
    if service1 is None:
        raise ValueError(f"Услуги {service} нет в базе данных услуг. Добавьте сначала туда.")
    master.specializations.append(service1)
    session.commit()

def add_new_master(telegram_id: int, experience_years: int, services: list[str], session=None):
    """
    Предполагаю, что мастер перед тем как стать мастером сначала взаимодествует с ботом, то есть он уже есть в БД как user.
    (Например нажимает кнопку стать мастером и пишет некоторый код, который получает от админа после собеса)
    Добавляет нового мастера, в списке services должны быть написаны названия услуг, которые УЖЕ лежат в БД услуг.
    Если там чего-то нет, то нужно сначала вызвать для них функцию add_new_service.
    (Предполагаю, что добавлять новое может только админ) А мастер только выбирает из существующего списка кнопками.
    """
    session = session or get_session()
    if check_new_user(telegram_id, session):
        raise ValueError("Такого пользователя нет в БД, сначала должен появится там!")
    user = session.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    if user.role == 'master':
        return
    user.role = 'master'
    master = models.Master(user_id=user.user_id, experience_years=experience_years)
    for service in services:
        add_service_to_master(master, service, session)

    session.add(master)
    session.commit()

def add_master_code(code: str, description: str, user_id: int = None, session=None):
    """
    Добавляет новый код мастера в базу данных, если такого кода ещё нет.
    """
    session = session or get_session()

    existing_code = session.query(models.MasterCode).filter_by(code=code).first()
    if existing_code:
        print(f"Код '{code}' уже существует в базе данных.")
        return

    master_code = models.MasterCode(code=code, description=description, user_id=user_id)
    session.add(master_code)
    session.commit()
    print(f"Код '{code}' успешно добавлен.")



def assign_master_code_to_user(user_id: int, code: str, session=None):
    """
    Сопоставляет пользователя с кодом мастера.
    """
    session = session or get_session()

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


def is_user_linked_to_code(user_id: int, code: str, session=None) -> bool:
    """
    Проверяет, связан ли пользователь с кодом мастера.
    """
    session = session or get_session()
    master_code = session.query(models.MasterCode).filter_by(code=code, user_id=user_id).first()
    return master_code is not None

def get_master_code_by_user_id(user_id: int, session=None) -> str | None:
    """
    Получает код мастера для конкретного пользователя.
    """
    master_code = session.query(models.MasterCode).filter_by(user_id=user_id).first()
    return master_code.code if master_code else None

def get_master_by_telegram_id(telegram_id: int, session = None) -> models.Master:
    session = session or get_session()
    user = session.query(models.User).filter(models.User.telegram_id == telegram_id).first()
    try:
        return user.master[0]
    except Exception:
        return None

def get_all_masters(session = None) -> typing.List[models.Master]:
    session = session or get_session()
    return session.query(models.Master).all()

def get_all_services(session = None) -> typing.List[models.Service]:
    session = session or get_session()
    return session.query(models.Service).all()

def get_service_by_appointment(appointment: models.Appointment, session = None) -> models.Service:
    return appointment.service

def get_services_by_master(master: models.Master, session = None) -> list[models.Service]:
    """
    Получить услуги, которые предоставляет мастер
    """
    return list(master.specializations)

def get_masters_by_service(service1: models.Service, session = None) -> list[models.Master]:
    return list(service1.masters)

def add_new_schedule_to_master(master: models.Master, start_time, end_time, session=None):
    """
    Время начала и конца должно быть кратно 30 минутам!
    Добавляет новый промежуток рабочего времени для мастера, если этот промежуток пересекается с уже существующим,
    то в базе будет храниться их объединение
    """
    session = session or get_session()
    lst = []
    begin = start_time
    end = start_time + datetime.timedelta(minutes=30)
    while end <= end_time:
        schedule_tmp = models.Schedule(master_id=master.master_id, start_time=begin, end_time=end)
        lst.append(schedule_tmp)
        begin += datetime.timedelta(minutes=30)
        end += datetime.timedelta(minutes=30)

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

def get_schedules_by_master(master: models.Master, session = None):
    """
    В БД хранятся равные промежутки по 30 минут (у каждого время начала кратно 30 минутам)
    """
    return master.schedule

def get_master_by_schedule(schedule: models.Schedule, session = None):
    return schedule.master

def get_schedules_by_service_and_master(master: models.Master, service: models.Service, session = None)->list[models.Schedule]:
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

def get_schedules_by_service(service: models.Service, session = None) -> dict[models.Master, list[models.Schedule]]:
    """
    Возвращает словарь Мастер - список промежутков времени, на которые возможна запись
    """
    res = {}
    session = session or get_session()
    for master in session.query(models.Master).all():
        res[master] = get_schedules_by_service_and_master(master, service, session=session)
    return res

def add_new_appointment(master: models.Master, user: models.User, service: models.Service, schedule: models.Schedule, session=None):
    """
    Делает новую запись, на дотупное время. Этот schedule должен быть получен при помощи 1 из 2х функций сверху.
    """
    session = session or get_session()
    app = models.Appointment(user_id = user.user_id, master_id=master.master_id, service_id=service.service_id,
                             start_time=schedule.start_time, end_time=schedule.start_time + datetime.timedelta(minutes=service.duration_minutes))
    session.add(app)
    session.commit()

def get_appointments_by_user(user: models.User, session = None) -> typing.List[models.Appointment]:
    return user.appointments

def get_appointments_by_master(master: models.Master, session = None) -> typing.List[models.Appointment]:
    return master.appointments

def cancel_appointment(appointment: models.Appointment, session=None):
    session = session or get_session()
    appointment.status = 'cancelled'
    session.commit()

def confirm_appointment(appointment: models.Appointment, session=None):
    session = session or get_session()
    appointment.status = 'confirmed'
    session.commit()

def get_appointment_by_id(appointment_id: int, session = None) -> models.Appointment:
    session = session or get_session()
    appo = session.query(models.Appointment).filter_by(appointment_id=appointment_id).first()
    return appo

def get_service_by_id(service_id: int, session = None) -> models.Service:
    session = session or get_session()
    serv = session.query(models.Service).filter_by(service_id=service_id).first()
    return serv

def get_master_by_master_id(master_id: int, session = None) -> models.Master:
    session = session or get_session()
    mast = session.query(models.Master).filter_by(master_id=master_id).first()
    return mast

def get_schedule_by_id(schedule_id: int, session = None) -> models.Schedule:
    session = session or get_session()
    sch = session.query(models.Schedule).filter_by(schedule_id=schedule_id).first()
    return sch

def get_master_by_appointment(appointment: models.Appointment, session = None) -> models.Master:
    return appointment.master

def make_notification(appointment: models.Appointment, type_: str, send_at: int = 3, chat_id: int = None, session=None):
    """
    type_: "reminder" or "confirmation"
    send_at - за сколько часов до записи.
    """
    session = session or get_session()
    notif = models.Notification(appointment_id = appointment.appointment_id, notification_type = type_,
                                send_at = appointment.start_time - datetime.timedelta(hours=send_at),
                                chat_id=chat_id)
    session.add(notif)
    session.commit()

def delete_master(master: models.Master, session = None):
    """
    Все эти функции удаления должны каскадом удалять все связанные записи.
    """
    session = session or get_session()
    session.delete(master)
    session.commit()

def delete_user(user: models.User, session = None):
    session = session or get_session()
    session.delete(user)
    session.commit()

def delete_service(service: models.Service, session = None):
    session = session or get_session()
    session.delete(service)
    session.commit()

def delete_notification(notification: models.Notification, session = None):
    session = session or get_session()
    session.delete(notification)
    session.commit()


