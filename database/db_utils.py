import re

import models
import json

from database.models import SessionLocal


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

def get_services_by_master(master: models.Master):
    """
    Получить услуги, которые предоставляет мастер
    """
    return list(master.specializations)

def get_masters_by_service(service1: models.Service):
    return list(service1.masters)

def add_new_schedule_to_master(master: models.Master, work_date, start_time, end_time):
    """
    Добавляет новый промежуток рабочего времени для мастера, если этот промежуток пересекается с уже существующим,
    то ничего не происходит.
    """
    with models.SessionLocal() as session:
        sch = session.query(models.Schedule).filter(models.Schedule.work_date == work_date).first()
        if not sch is None:
            if sch.start_time < start_time < sch.end_time:
                return
            if start_time < sch.start_time < end_time:
                return
        schedule = models.Schedule(master_id=master.master_id, work_date=work_date, start_time=start_time, end_time=end_time)
        session.add(schedule)
        session.commit()

def get_schedules_by_master(master: models.Master):
    return master.schedule

def get_master_by_schedule(schedule: models.Schedule):
    return schedule.master

def get_schedules_by_service_and_master():
    """
    доступные промежутки по данной услуге и мастеру
    :return:
    """
    pass

def get_schedules_by_service():
    """
    доступные промежутки по данной услуге
    """
    pass

def add_new_appointment(master_id: int, user_id: int, service_id, start_time):
    """
    Новую запись
    """
    pass

