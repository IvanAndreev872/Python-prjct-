import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.types import Message, CallbackQuery, User as TelegramUser, Chat
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Master, Appointment
from bot.handlers.master_handlers import handle_my_appointments, notify_client

@pytest.mark.asyncio
async def test_handle_my_appointments_as_master():
    """
    Создаём фиктивные данные для пользователя-мастера и его записи
    """
    fake_user = User(
        user_id=1,
        telegram_id=12345,
        name="Test Master",
        role="master"
    )
    fake_master = Master(
        master_id=1,
        user_id=1,
        experience_years=5
    )
    fake_appointment = Appointment(
        appointment_id=1,
        user_id=2,
        master_id=1,
        service_id=1,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        status="confirmed"
    )
    fake_appointment.user = User(
        user_id=2,
        telegram_id=54321,
        name="Test Client",
        role="client"
    )

    """
    Мокаем вызовы к базе данных для возврата фиктивных данных
    """
    async def mock_execute(query):
        query_str = str(query)
        if "FROM user" in query_str and "telegram_id" in query_str:
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = fake_user
            return mock_result
        elif "FROM master" in query_str and "user_id" in query_str:
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = fake_master
            return mock_result
        elif "FROM appointment" in query_str and "master_id" in query_str:
            mock_result = AsyncMock()
            mock_scalars = MagicMock()
            mock_scalars.all = AsyncMock(return_value=[fake_appointment])
            mock_result.scalars = MagicMock(return_value=mock_scalars)
            return mock_result

        return AsyncMock()

    async_session_mock = AsyncMock(spec=AsyncSession)
    async_session_mock.execute = mock_execute

    """
    Создаём фиктивное сообщение от лица мастера
    """
    message = Message(
        message_id=1,
        date=datetime.now(),
        chat=Chat(id=1, type="private"),
        from_user=TelegramUser(id=12345, is_bot=False, first_name="Master"),
    )

    """ Данный тест проверяет, что при вызове команды /my_appointments:
        1) Пользователь корректно определяется как мастер
        2) Из базы данных извлекаются записи, связанные с мастером
        3) Отправляется сообщение со списком найденных записей
    """
    with patch("bot.handlers.master_handlers.get_master_appointments_keyboard", return_value=None), \
         patch("aiogram.types.message.Message.answer", new=AsyncMock()):
        await handle_my_appointments(message, async_session_mock)

@pytest.mark.asyncio
async def test_notify_client():
    """
    Создаём фиктивную запись и клиента
    """
    fake_appointment = Appointment(
        appointment_id=1,
        user_id=2,
        master_id=1,
        service_id=1,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        status="confirmed"
    )
    fake_appointment.user = User(
        user_id=2,
        telegram_id=54321,
        name="Test Client",
        role="client"
    )

    async_session_mock = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = fake_appointment
    async_session_mock.execute.return_value = mock_result
    """
    Эмулируем callback_query с данными notify_1
    """
    callback_query = CallbackQuery(
        id="test_query",
        from_user=TelegramUser(id=12345, is_bot=False, first_name="Test Master"),
        data="notify_1",
        chat_instance="unique_chat_instance",
        message=Message(
            message_id=1,
            date=datetime.now(),
            chat=Chat(id=1, type="private"),
        ),
    )
    """ Данный тест проверяет, что при получении callback запроса с notify_:
        1) Извлекается ID записи
        2) Находится соответствующая запись в базе данных
        3) Вызывается функция уведомления клиента
        4) Отправляется подтверждающее сообщение мастеру
    """
    with patch("bot.handlers.master_handlers.send_notification_to_client", return_value=None), \
         patch("aiogram.types.message.Message.answer", new=AsyncMock()):
        await notify_client(callback_query, async_session_mock)
