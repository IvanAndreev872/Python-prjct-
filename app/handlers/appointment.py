from aiogram import  F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import database.db_utils as db_utils
import app.keyboards.appointment_kb as appointment_kb
import app.keyboards.welcome_keyboard as welcome_keyboard
import app.keyboards.registered_users_kb as registered_users_kb

router = Router()

class Appointment(StatesGroup) :
    choose_master = State()
    choose_service = State()

@router.message(F.text.lower() == 'отмена')
async def cancel_handler(message: Message, state: FSMContext):
    """
    Отменяет запись
    """
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.clear()
    await message.answer(text='Регистрация прекращена.', reply_markup=registered_users_kb.regist(message.from_user.id))

'''@router.message(F.text.lower == 'записаться на процедуру')
async def start_appointment(message: Message, state: FSMContext):'''
