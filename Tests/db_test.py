from datetime import datetime

import pytest
import datetime
from sqlalchemy.orm import sessionmaker

import database.db_utils as db_utils
import database.models as models

@pytest.fixture(scope='session')
def engine():
    return models.sa.create_engine("sqlite+pysqlite:///:memory:")

@pytest.fixture(scope='session')
def tables(engine):
    models.Base.metadata.create_all(engine)
    yield
    models.Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session_mk = sessionmaker(bind=engine)
    session = Session_mk()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function', autouse=True)
def cleanup_database(session):
    yield
    for table in reversed(models.Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()

@pytest.fixture
def db_some_users(session):
    db_utils.add_new_user(telegram_id=1234, name="Peter", phone="79997558557", email="abga@gmaig.com", session=session)
    db_utils.add_new_user(telegram_id=2234, name="Alex", phone="795771", email="agmaig.com", session=session)
    db_utils.add_new_user(telegram_id=3235, name="Mary", phone="7957854984", email="agma@ig.com", session=session)


def test_user_adding(session):
    usr1 = models.User(telegram_id=1234, name = "Peter", phone="79997558557", email="abga@gmaig.com")
    usr2 = models.User(telegram_id=2234, name = "Alex", phone="7957", email="agmaig.com")
    usr3 = models.User(telegram_id=2234, name = "Max", phone="79579898484", email="agm@aig.com")

    db_utils.add_new_user(telegram_id=1234, name = "Peter", phone="79997558557", email="abga@gmaig.com", session=session)
    db_utils.add_new_user(telegram_id=2234, name = "Alex", phone="7957", email="agmaig.com", session=session)
    usr3_2 = db_utils.add_new_user(telegram_id=2234, name = "Max", phone="79579898484", email="agm@aig.com", session=session)

    usr1_2 = session.query(models.User).filter(models.User.telegram_id == usr1.telegram_id).first()
    usr2_2 = session.query(models.User).filter(models.User.telegram_id == usr2.telegram_id).first()

    assert usr1_2 is not None
    assert usr2_2 is not None
    assert usr3_2 is None
    lst1 = [usr1, usr2]
    lst2 = [usr1_2, usr2_2]
    for u1, u2 in zip(lst1, lst2):
        assert u1.telegram_id == u2.telegram_id
        assert u1.name == u2.name


def test_get_user_by_telegram_id(session, db_some_users):
    usr1 = db_utils.get_user_by_telegram_id(telegram_id=1234, session=session)
    assert usr1 is not None
    assert usr1.name == "Peter"
    assert usr1.phone == "79997558557"

def test_add_new_service(session):
    db_utils.add_new_service(name='Cutting', description='bla bla', price=5000, duration_minutes=60, session=session)

    serv = session.query(models.Service).filter(models.Service.name == 'Cutting').first()
    assert serv is not None
    assert serv.description == 'bla bla'
    assert serv.price == 5000
    assert serv.duration_minutes == 60

@pytest.fixture(scope='function')
def db_services(session, db_some_users):
    db_utils.add_new_service(name='Cutting', description='bla bla', price=5000, duration_minutes=60, session=session)
    db_utils.add_new_service(name='Manicure', description='bla bla', price=7000, duration_minutes=90, session=session)
    db_utils.add_new_service(name='Massage', description='bla bla', price=8000, duration_minutes=60, session=session)

def test_get_service_by_name(session, db_services):
    serv = db_utils.get_service_by_name('Cutting', session=session)
    assert serv is not None
    assert serv.description == 'bla bla'
    assert serv.price == 5000


def test_add_new_master(session, db_services):
    db_utils.add_new_master(telegram_id=1234, experience_years=4, services=['Cutting', 'Manicure'], session=session)

    master = session.query(models.Master).first()
    assert master is not None
    assert master.experience_years == 4

@pytest.fixture
def db_masters(session, db_services):
    db_utils.add_new_master(telegram_id=1234, experience_years=4, services=['Cutting', 'Manicure'], session=session)
    db_utils.add_new_master(telegram_id=2234, experience_years=5, services=['Cutting', 'Massage'], session=session)

def test_get_master_by_telegram_id(session, db_masters):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    assert master is not None
    assert master.experience_years == 4

def test_get_user_by_master(session, db_masters):
    master  = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    user = db_utils.get_user_by_master(master, session=session)
    assert user is not None
    assert user.name == "Peter"

def test_get_services_by_master(session, db_masters):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    services = db_utils.get_services_by_master(master=master, session=session)
    assert services is not None
    assert len(services) == 2
    assert services[0].name == "Cutting"
    assert services[1].name == "Manicure"

def test_add_service_to_master(session, db_masters):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    db_utils.add_service_to_master(master, 'Massage', session=session)
    services = db_utils.get_services_by_master(master=master, session=session)
    assert services is not None
    assert len(services) == 3
    assert services[-1].name == "Massage"


def test_get_masters_by_service(session, db_masters):
    service = db_utils.get_service_by_name('Cutting', session=session)
    masters = db_utils.get_masters_by_service(service, session=session)
    assert masters is not None
    assert len(masters) == 2
    assert db_utils.get_user_by_master(masters[0]).name == "Peter"
    assert db_utils.get_user_by_master(masters[1]).name == "Alex"
    service2 = db_utils.get_service_by_name('Manicure', session=session)
    masters2 = db_utils.get_masters_by_service(service2, session=session)
    assert masters2 is not None
    assert len(masters2) == 1
    assert db_utils.get_user_by_master(masters2[0]).name == "Peter"

def test_add_new_schedule_to_master(session, db_masters):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    db_utils.add_new_schedule_to_master(master=master,
                                        start_time=datetime.datetime(year=2024, month=1, day=1, hour = 10),
                                        end_time=datetime.datetime(year=2024, month=1, day=1, hour=18),
                                        session=session)
    schedules = master.schedule
    assert schedules is not None
    assert len(schedules) == (18 - 10) * 2
    assert schedules[0].start_time == datetime.datetime(year=2024, month=1, day=1, hour=10)
    assert schedules[-1].start_time == datetime.datetime(year=2024, month=1, day=1, hour=17, minute=30)

@pytest.fixture
def db_schedules(session, db_masters):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    master2 = db_utils.get_master_by_telegram_id(telegram_id=2234, session=session)
    db_utils.add_new_schedule_to_master(master=master,
                                        start_time=datetime.datetime(year=2024, month=12, day=20, hour=10),
                                        end_time=datetime.datetime(year=2024, month=12, day=20, hour=18),
                                        session=session)
    db_utils.add_new_schedule_to_master(master=master,
                                        start_time=datetime.datetime(year=2024, month=12, day=21, hour=13),
                                        end_time=datetime.datetime(year=2024, month=12, day=21, hour=16),
                                        session=session)
    db_utils.add_new_schedule_to_master(master=master2,
                                        start_time=datetime.datetime(year=2024, month=12, day=21, hour=10),
                                        end_time=datetime.datetime(year=2024, month=12, day=21, hour=14, minute=30),
                                        session=session)

def test_get_schedules_by_master(session, db_schedules):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    schedules = db_utils.get_schedules_by_master(master=master, session=session)
    assert schedules is not None
    assert len(schedules) == (18 - 10) * 2 + (16 - 13) * 2
    assert schedules[0].start_time == datetime.datetime(year=2024, month=12, day=20, hour=10)
    assert schedules[-1].start_time == datetime.datetime(year=2024, month=12, day=21, hour=15, minute=30)


def test_get_master_by_schedule(session, db_schedules):
    schedule = session.query(models.Schedule).first()
    master = db_utils.get_master_by_schedule(schedule, session=session)
    assert master is not None
    assert db_utils.get_user_by_master(master).name == "Peter"

def test_get_schedules_by_service_and_master(session, db_schedules):
    service = db_utils.get_service_by_name('Cutting', session=session)
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    schedules = db_utils.get_schedules_by_service_and_master(master, service, session=session)
    assert schedules is not None
    assert len(schedules) == (18 - 10) * 2 + (16 - 13) * 2 - 2
    assert schedules[-1].start_time == datetime.datetime(year=2024, month=12, day=21, hour=15)

def test_get_schedules_by_service(session, db_schedules):
    service = db_utils.get_service_by_name('Cutting', session=session)
    schedules = db_utils.get_schedules_by_service(service, session=session)
    master1 = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    master2 = db_utils.get_master_by_telegram_id(telegram_id=2234, session=session)
    assert schedules is not None
    assert len(schedules) == 2
    assert len(schedules[master1]) == (18 - 10) * 2 + (16 - 13) * 2 - 2
    assert len(schedules[master2]) == (14 - 10) * 2

def test_add_new_appointment(session, db_schedules):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    user = db_utils.get_user_by_telegram_id(telegram_id=3235, session=session)
    service = db_utils.get_service_by_name('Cutting', session=session)
    l1 = len(db_utils.get_schedules_by_service_and_master(master, service, session=session))
    schedule = db_utils.get_schedules_by_service_and_master(master, service, session=session)[0]
    db_utils.add_new_appointment(master, user, service, schedule, session=session)
    l2 = len(db_utils.get_schedules_by_service_and_master(master, service, session=session))

    appointment = session.query(models.Appointment).first()
    assert appointment is not None
    assert appointment.user == user
    assert appointment.service == service
    assert appointment.start_time == schedule.start_time
    assert l1 - 2 == l2

@pytest.fixture
def db_appointments(session, db_schedules):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    master2 = db_utils.get_master_by_telegram_id(telegram_id=2234, session=session)
    user = db_utils.get_user_by_telegram_id(telegram_id=3235, session=session)
    service = db_utils.get_service_by_name('Cutting', session=session)
    schedule1 = db_utils.get_schedules_by_service_and_master(master, service, session=session)[0]
    schedule2 = db_utils.get_schedules_by_service_and_master(master, service, session=session)[0]
    schedule3 = db_utils.get_schedules_by_service_and_master(master2, service, session=session)[0]
    db_utils.add_new_appointment(master, user, service, schedule1, session=session)
    db_utils.add_new_appointment(master, user, service, schedule2, session=session)
    db_utils.add_new_appointment(master2, user, service, schedule3, session=session)

def test_get_service_by_appointment(session, db_appointments):
    appointment = session.query(models.Appointment).first()
    service = db_utils.get_service_by_appointment(appointment, session=session)
    assert service is not None
    assert service.name == "Cutting"

def test_get_appointments_by_user(session, db_appointments):
    user = db_utils.get_user_by_telegram_id(telegram_id=3235, session=session)
    appointments = db_utils.get_appointments_by_user(user, session=session)
    assert appointments is not None
    assert len(appointments) == 3

def test_get_appointments_by_master(session, db_appointments):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    appointments = db_utils.get_appointments_by_master(master, session=session)
    assert appointments is not None
    assert len(appointments) == 2

def test_cancel_appointment(session, db_appointments):
    appointment = session.query(models.Appointment).first()
    assert appointment.status == 'pending'
    db_utils.cancel_appointment(appointment, session=session)
    assert appointment.status == 'cancelled'

def test_confirm_appointment(session, db_appointments):
    appointment = session.query(models.Appointment).first()
    assert appointment.status == 'pending'
    db_utils.confirm_appointment(appointment, session=session)
    assert appointment.status == 'confirmed'

def test_get_appointment_by_id(session, db_appointments):
    appo1 = session.query(models.Appointment).filter(models.Appointment.appointment_id == 1).first()
    appo3 = session.query(models.Appointment).filter(models.Appointment.appointment_id == 3).first()
    appo1_2 = db_utils.get_appointment_by_id(1, session=session)
    appo3_2 = db_utils.get_appointment_by_id(3, session=session)
    assert appo1.appointment_id == appo1_2.appointment_id
    assert appo3.appointment_id == appo3_2.appointment_id

def test_get_master_by_appointment(session, db_appointments):
    appointment = session.query(models.Appointment).first()
    master1 = db_utils.get_master_by_appointment(appointment, session=session)
    master2 = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    assert master1 == master2

def test_make_notification(session, db_appointments):
    appo = session.query(models.Appointment).first()
    db_utils.make_notification(appo, type_='reminder', send_at=2, session=session)
    notif = session.query(models.Notification).first()
    assert notif is not None
    assert notif.notification_type == 'reminder'
    assert notif.appointment_id == appo.appointment_id

@pytest.fixture
def db_notifications(session, db_appointments):
    appo = session.query(models.Appointment).all()
    db_utils.make_notification(appo[0], type_='reminder', send_at=2, session=session)
    db_utils.make_notification(appo[1], type_='confirmation', send_at=3, session=session)

def test_delete_master(session, db_appointments):
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    db_utils.delete_master(master, session=session)
    master2 = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    schedules = session.query(models.Schedule).filter(models.Schedule.master_id == master.master_id).first()
    appointments = session.query(models.Appointment).filter(models.Appointment.master_id == master.master_id).first()
    service = db_utils.get_service_by_name('Manicure', session=session)
    masters = db_utils.get_masters_by_service(service, session=session)
    assert master2 is None
    assert schedules is None
    assert appointments is None
    assert masters == []


def test_delete_user(session, db_appointments):
    user = db_utils.get_user_by_telegram_id(telegram_id=1234, session=session)
    db_utils.delete_user(user, session=session)
    user2 = db_utils.get_user_by_telegram_id(telegram_id=1234, session=session)
    appointments = session.query(models.Appointment).filter(models.Appointment.user_id == user.user_id).first()
    master = db_utils.get_master_by_telegram_id(telegram_id=1234, session=session)
    assert user2 is None
    assert appointments is None
    assert master is None

def test_delete_service(session, db_appointments):
    service = db_utils.get_service_by_name('Manicure', session=session)
    db_utils.delete_service(service, session=session)
    service2 = db_utils.get_service_by_name('Manicure', session=session)
    assert service2 is None
    appointments = session.query(models.Appointment).filter(models.Appointment.service_id == service.service_id).first()
    assert appointments is None