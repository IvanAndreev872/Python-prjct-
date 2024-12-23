from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from bot.keyboards.welcome_keyboard import get_welcome_kb
from database import db_utils

router = Router()

class MasterFSM(StatesGroup):
    awaiting_code = State()

@router.message(CommandStart())
async def command_start_handler(message: Message):
    """
    Выдает кнопку регистрации, только если юзера с таким ID нет в нашей БД.
    """
    kb = get_welcome_kb(message.from_user.id)
    await message.answer("Здравствуйте! Выберите действие:", reply_markup=kb)

@router.message(F.text == "Стать мастером")
async def become_master_handler(message: Message, state: FSMContext):
    """
    Обработчик кнопки "Стать мастером".
    """
    user_id = message.from_user.id
    user = db_utils.get_user_by_telegram_id(user_id)

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
    """
    secret_code = message.text.strip()
    user_id = message.from_user.id
    user = db_utils.get_user_by_telegram_id(user_id)

    if not user:
        await message.answer("Вы не зарегистрированы.")
        await state.clear()
        return

    if user.role == "master":
        await message.answer("Вы уже являетесь мастером.")
        await state.clear()
        return

    master_code = db_utils.get_master_code(secret_code)
    if not master_code or master_code.user_id:
        await message.answer("Неверный код. Попробуйте ещё раз.")
        return

    # Присвоение роли мастера
    db_utils.add_new_master(user.telegram_id, experience_years=0, services=[])
    db_utils.assign_master_code_to_user(user.user_id, secret_code)

    await message.answer("Вы успешно стали мастером! Настройте свои услуги и график.")
    await state.clear()
