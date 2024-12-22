import pytest
import aiogram
from aiogram import Dispatcher
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, SendContact, AnswerCallbackQuery, EditMessageText
from aiogram.methods.base import TelegramType
from sqlalchemy import Update
from sqlalchemy.orm import Session
import aiogram.types
import database.models as models
import datetime
import database.db_utils as db_utils
from Tests.Bot_tests.conftest import session
from Tests.Bot_tests.mocked_aiogram import MockedBot
import app.handlers.registration
import app.handlers.my_appointments
from registration_test import make_message

@pytest.fixture(scope="function")
def some_data(session):
    db_utils.add_new_user(telegram_id=1234, name="Me", phone="79997558557", email="abga@gmaig.com", session=session)
    db_utils.add_new_user(telegram_id=2234, name="Alex", phone="795771", email="agmaig.com", session=session)
    db_utils.add_new_service(name='Cutting', description='bla bla', price=5000, duration_minutes=60, session=session)
    db_utils.add_new_service(name='Manicure', description='bla bla', price=7000, duration_minutes=90, session=session)
    db_utils.add_new_service(name='Massage', description='bla bla', price=8000, duration_minutes=60, session=session)
    db_utils.add_new_master(telegram_id=2234, experience_years=5, services=['Cutting', 'Massage'], session=session)
    master = db_utils.get_master_by_telegram_id(telegram_id=2234, session=session)
    db_utils.add_new_schedule_to_master(master=master,
                                        start_time=datetime.datetime(year=2025, month=1, day=20, hour=10),
                                        end_time=datetime.datetime(year=2025, month=1, day=20, hour=19),
                                        session=session)
    user = db_utils.get_user_by_telegram_id(telegram_id=1234, session=session)
    service = db_utils.get_service_by_name('Cutting', session=session)
    schedule1 = db_utils.get_schedules_by_service_and_master(master, service, session=session)[0]
    db_utils.add_new_appointment(master, user, service, schedule1, session=session)


def make_callback(user_id, data):
    user = aiogram.types.User(id=user_id, first_name='User', is_bot=False)
    message = make_message(user_id, '-')
    return aiogram.types.CallbackQuery(from_user=user, id='22111001111333', chat_instance='34444444443234', data=data, message=message)


@pytest.mark.asyncio
async def test_get_appointments(dp: Dispatcher, bot: MockedBot, some_data):
    user_id = 1234
    master_id = 2234
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    result = await dp.feed_update(bot,
                                  aiogram.types.Update(message=make_message(user_id, 'мои записи'), update_id=1))
    assert result is not UNHANDLED
    outgoing_message: TelegramType = bot.get_request()
    assert outgoing_message.reply_markup is not None
    markup = outgoing_message.reply_markup
    assert isinstance(markup, aiogram.types.InlineKeyboardMarkup)
    assert markup.inline_keyboard[0][0].text.startswith('Cutting - 2025')


@pytest.mark.asyncio
async def test_state_and_cancel(dp: Dispatcher, bot: MockedBot, some_data):
    user_id = 1234
    master_id = 2234
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(None)

    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    await dp.feed_update(bot,
                        aiogram.types.Update(message=make_message(user_id, 'мои записи'), update_id=1))

    outgoing_message: TelegramType = bot.get_request()
    current_state = await fsm_context.get_state()
    assert current_state == app.handlers.my_appointments.AppointmentsStates.choosing_appointment

    bot.add_result_for(
        method=EditMessageText,
        ok=True
    )
    bot.add_result_for(method=AnswerCallbackQuery, ok=True)
    callback = make_callback(user_id, '1')
    update = await dp.feed_update(bot, aiogram.types.Update(callback_query=callback, update_id=1))
    assert update is not UNHANDLED

    outgoing_message: TelegramType = bot.get_request()
    current_state = await fsm_context.get_state()
    assert current_state == app.handlers.my_appointments.AppointmentsStates.pressing_button
    assert outgoing_message.text.startswith('Подробности')

    bot.get_request()

    callback2 = make_callback(user_id, 'cancel_1')
    bot.add_result_for(
        method=EditMessageText,
        ok=True
    )
    bot.add_result_for(method=AnswerCallbackQuery, ok=True)
    update = await dp.feed_update(bot, aiogram.types.Update(callback_query=callback2, update_id=2))
    assert update is not UNHANDLED
    outgoing_message: TelegramType = bot.get_request()
    current_state = await fsm_context.get_state()
    assert current_state == app.handlers.my_appointments.AppointmentsStates.choosing_appointment
    assert outgoing_message.text == 'Запись отменена.'

    user = db_utils.get_user_by_telegram_id(telegram_id=user_id)
    assert db_utils.get_appointments_by_user(user)[0].status == 'cancelled'
