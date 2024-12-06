import pytest
from sqlalchemy import event
from sqlalchemy.orm import scoped_session, sessionmaker, Session

import database.db_utils as db_utils
import database.models as models

class TestSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.begin_nested()

        @event.listens_for(self, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                session.expire_all()
                session.begin_nested()

Session = scoped_session(sessionmaker(autoflush=False, class_=TestSession))


@pytest.fixture(scope='session')
def engine():
    engine = models.sa.create_engine('sqlite+pysqlite:///:memory:', echo=False)
    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        models.Base.metadata.drop_all(engine, checkfirst=True)

@pytest.fixture
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()

    Session.configure(bind=engine)
    session = Session()

    try:
        yield session
    finally:
        Session.remove()
        transaction.rollback()
        connection.close()


def user_adding_test(session):
    usr1 = models.User(telegram_id=11, name = "Peter", phone="79997558557", email="abga@gmaig.com")
    usr2 = models.User(telegram_id=12, name = "Alex", phone="7957", email="agmaig.com")
    usr3 = models.User(telegram_id=12, name = "Max", phone="79579898484", email="agm@aig.com")

    db_utils.add_new_user(telegram_id=11, name = "Peter", phone="79997558557", email="abga@gmaig.com")
    db_utils.add_new_user(telegram_id=12, name = "Alex", phone="7957", email="agmaig.com")
    db_utils.add_new_user(telegram_id=12, name = "Max", phone="79579898484", email="agm@aig.com")


    usr1_2 = session.query(models.User).filter(models.User.telegram_id == usr1.telegram_id).first()
    usr2_2 = session.query(models.User).filter(models.User.telegram_id == usr2.telegram_id).first()
    usr3_2 = session.query(models.User).filter(models.User.telegram_id == usr3.telegram_id).first()

    assert usr1_2 is not None
    assert usr2_2 is not None
    assert usr3_2 is None
    assert usr1 == usr1_2
    assert usr2 == usr2_2

