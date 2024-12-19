from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup

from app.keyboards.registered_users_kb import get_registered_kb
from app.keyboards.welcome_keyboard import get_welcome_kb
from database import db_utils

import asyncio

router = Router()

class MasterFSM(StatesGroup):
    awaiting_code = State()

"""
хэндлер начала работы, принимает на вход "/start"
"""

@router.message(CommandStart())
async def command_start_handler(message: Message):
    """
    Выдает кнопку регистрации, только если юзера с таким ID нет в нашей БД.
    Поскольку get_welcome_kb синхронная, вызываем её через to_thread.
    """
    kb = get_welcome_kb(message.from_user.id)
    await message.answer("Здравствуйте!", reply_markup=kb)


@router.message(F.text == "Стать мастером")
async def become_master_handler(message: Message, state: FSMContext):
    """
    Обработчик кнопки "Стать мастером". Проверяем регистрацию синхронно, но в отдельном потоке.
    """
    user_id = message.from_user.id
    user = await asyncio.to_thread(db_utils.get_user_by_telegram_id, user_id)

    if not user:
        await message.answer("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь сначала.")
        return

    if user.role == "master":
        await message.answer("Вы уже являетесь мастером.")
        return

    await state.set_state(MasterFSM.awaiting_code)
    await message.answer("Введите секретный код, предоставленный администратором:")


@router.message(F.text, MasterFSM.awaiting_code)
async def handle_master_code(message: Message, state: FSMContext):
    """
    Обработчик ввода секретного кода.
    Все проверки кода и изменение роли делаем через to_thread.
    """
    secret_code = message.text.strip()
    user_id = message.from_user.id
    user = await asyncio.to_thread(db_utils.get_user_by_telegram_id, user_id)

    if not user:
        await message.answer("Вы не зарегистрированы.")
        await state.clear()
        return

    if user.role == "master":
        await message.answer("Вы уже являетесь мастером.")
        await state.clear()
        return

    master_code = await asyncio.to_thread(db_utils.get_master_code, secret_code)
    if not master_code or master_code.user_id:
        await message.answer("Неверный код. Попробуйте ещё раз.")
        return

    # Присвоение роли мастера и привязка кода
    await asyncio.to_thread(db_utils.add_new_master, user.telegram_id, 0, [])
    await asyncio.to_thread(db_utils.bind_master_code_to_user, secret_code, user.user_id)

    await message.answer("Вы успешно стали мастером! Настройте свои услуги и график.")
    await state.clear()


@router.message(F.text == "Экран мастера")
async def redirect_to_master_screen(message: Message):
    """
    Перенаправляет пользователя на экран мастера.
    Проверяем роль юзера в отдельном потоке, затем синхронно вызываем handle_my_appointments.
    """
    user_id = message.from_user.id
    user = await asyncio.to_thread(db_utils.get_user_by_telegram_id, user_id)

    if not user or user.role != "master":
        await message.answer("У вас нет доступа к экрану мастера.")
        return

@router.message(F.text == "Главное меню")
async def main_menu_handler(message: Message):
    kb = get_registered_kb()
    await message.answer(text='Меню клиента:', reply_markup=kb)
