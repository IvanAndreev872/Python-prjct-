

import pytest

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import create_engine
from database import models
from Tests.Bot_tests.mocked_aiogram import MockedBot, MockedSession
from app.middlewares.session_control import SessionControlMiddleware
from sqlalchemy.orm import sessionmaker

from app.handlers.welcome_handler import router as router_welcome
from app.handlers.registration import router as router_registration
from app.handlers.my_appointments import router as router_my_appointments

all_routers = [router_welcome, router_registration, router_my_appointments]

@pytest.fixture(scope='function')
def engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
    yield engine
    engine.dispose()

@pytest.fixture(scope='function')
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

attached = False

@pytest.fixture(scope="function")
def dp(session) -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.update.middleware(SessionControlMiddleware(session=session))
    global attached
    if not attached:
        dispatcher.include_routers(*all_routers)
        attached = True
    yield dispatcher
    dispatcher.storage.close()
    dispatcher.shutdown()
    dispatcher = None

@pytest.fixture(scope="function")
def bot() -> MockedBot:
    #Несуществующий токен. Имеет такой вид, чтобы проходил валидацию
    bot = MockedBot(token='7513777902:ABH7xoLvJtXg2-J9uC1XA3t2YT5zHlN5Jjk')
    bot.session = MockedSession()
    yield bot
    bot = None

@pytest.fixture(scope='function', autouse=True)
def cleanup_database(session, dp, bot):
    yield
    for table in reversed(models.Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()