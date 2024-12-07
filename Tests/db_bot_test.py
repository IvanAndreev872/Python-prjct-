import pytest
import aiogram
from aiogram import Dispatcher
from aiogram.dispatcher.event.bases import UNHANDLED
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.methods.base import TelegramType
from sqlalchemy import Update
from sqlalchemy.orm import Session

import database.models as models
import datetime

from Tests.mocked_aiogram import MockedBot
import app


def make_message(user_id: int, text: str) -> aiogram.types.Message:
    user = aiogram.types.User(id=user_id, first_name='User', is_bot=False)
    chat = aiogram.types.Chat(id=user_id, type=aiogram.enums.ChatType.PRIVATE)
    return aiogram.types.Message(message_id=1, from_user=user, chat=chat, text=text, date=datetime.datetime.now())

@pytest.mark.asyncio
async def test_cmd_start(dp: Dispatcher, bot: MockedBot):
    '''
    тест случая, когда пользователь не зареган
    '''
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

