import pytest
import aiogram
from aiogram import Dispatcher
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage, SendContact
from aiogram.methods.base import TelegramType
from sqlalchemy import Update
from sqlalchemy.orm import Session
import aiogram.types
import database.models as models
import datetime
import database.db_utils as db_utils

from Tests.Bot_tests.mocked_aiogram import MockedBot
import app.handlers.registration


def make_message(user_id: int, text: str) -> aiogram.types.Message:
    user = aiogram.types.User(id=user_id, first_name='User', is_bot=False)
    chat = aiogram.types.Chat(id=user_id, type=aiogram.enums.ChatType.PRIVATE)
    return aiogram.types.Message(message_id=1, from_user=user, chat=chat, text=text, date=datetime.datetime.now())


@pytest.mark.asyncio
async def test_cmd_start(dp: Dispatcher, bot: MockedBot):
    
    #тест случая, когда пользователь не зареган
    
    bot.add_result_for(
        method=SendMessage,
        ok=True,
    )
    result = await dp.feed_update(bot,
                                  aiogram.types.Update(message=make_message(1234, '/start'), update_id=1))
    assert result is not UNHANDLED
    outgoing_message: TelegramType = bot.get_request()
    assert isinstance(outgoing_message, SendMessage)
    assert outgoing_message.text == 'Здравствуйте!'
    assert outgoing_message.reply_markup is not None
    markup = outgoing_message.reply_markup
    assert isinstance(markup, aiogram.types.ReplyKeyboardMarkup)
    assert markup.keyboard[0][0].text == 'Регистрация'


def make_contact(user_id: int):
    contact = aiogram.types.Contact(id=user_id, first_name='User', is_bot=False, phone_number='+7900807560')
    user = aiogram.types.User(id=user_id, first_name='User', is_bot=False)
    chat = aiogram.types.Chat(id=user_id, type=aiogram.enums.ChatType.PRIVATE)
    return aiogram.types.Message(message_id=1, from_user=user, chat=chat, date=datetime.datetime.now(), contact=contact)

@pytest.mark.asyncio
async def test_states(dp: Dispatcher, bot: MockedBot):
    user_id = 123467
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(None)

    flow_messages = [
        make_message(user_id, '/start'),
        make_message(user_id, 'Регистрация'),
    ]
    for message in flow_messages:
        bot.add_result_for(method=SendMessage, ok=True)
        await dp.feed_update(bot, aiogram.types.Update(message=message, update_id=1))
        bot.get_request()

    current_state = await fsm_context.get_state()
    assert current_state == app.handlers.registration.Registration.writing_name

    bot.add_result_for(method=SendMessage, ok=True)
    await dp.feed_update(bot, aiogram.types.Update(message=make_message(user_id, "Bob"), update_id=1))
    bot.get_request()

    current_state = await fsm_context.get_state()
    assert current_state == app.handlers.registration.Registration.writing_email

    bot.add_result_for(method=SendMessage, ok=True)
    await dp.feed_update(bot, aiogram.types.Update(message=make_message(user_id, 'abc@gmail.com'), update_id=1))
    bot.get_request()

    current_state = await fsm_context.get_state()
    assert current_state == app.handlers.registration.Registration.sending_contact

    bot.add_result_for(method=SendContact, ok=True)
    await dp.feed_update(bot, aiogram.types.Update(message=make_contact(user_id), update_id=1))

    answer = bot.get_request()
    assert isinstance(answer, SendMessage)
    assert answer.text == "Вы прислали не свой контакт. Пришлите свой:"

@pytest.mark.asyncio
async def test_cancel(dp: Dispatcher, bot: MockedBot):
    user_id = 123467
    fsm_context: FSMContext = dp.fsm.get_context(bot=bot, user_id=user_id, chat_id=user_id)
    await fsm_context.set_state(None)

    flow_messages = [
        make_message(user_id, '/start'),
        make_message(user_id, 'Регистрация'),
        make_message(user_id, "Bob"),
        make_message(user_id, 'Отмена'),
    ]
    for message in flow_messages:
        bot.add_result_for(method=SendMessage, ok=True)
        await dp.feed_update(bot, aiogram.types.Update(message=message, update_id=1))
        bot.get_request()
    
    state = await fsm_context.get_state()
    assert state is None


@pytest.mark.asyncio
async def test_adding_to_db(dp: Dispatcher, bot: MockedBot):
    user_id = 4325111234
    flow_messages = [
        make_message(user_id, '/start'),
        make_message(user_id, 'Регистрация'),
        make_message(user_id, "Bob"),
        make_message(user_id, 'abc@gmail.com'),
        make_contact(user_id)
    ]
    for message in flow_messages:
        bot.add_result_for(method=SendMessage, ok=True)
        await dp.feed_update(bot, aiogram.types.Update(message=message, update_id=1))
        bot.get_request()

    added = db_utils.check_new_user(user_id)
    assert not added is None
