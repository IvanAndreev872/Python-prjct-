from aiogram import  F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram import types
import database.db_utils as db_utils
import app.keyboards.my_appointments_kb as my_appointments_kb

router = Router()

class AppointmentsStates(StatesGroup):
    choosing_appointment = State()
    pressing_button = State()


@router.message(F.text.lower().strip() == 'мои записи')
async def appointments_handler(message: types.Message, state: FSMContext):
    user = db_utils.get_user_by_telegram_id(message.from_user.id)
    appointments = db_utils.get_appointments_by_user(user)
    kb = my_appointments_kb.get_appointments_kb(appointments)
    await message.answer(text='Мои записи:', reply_markup=kb)
    await state.set_state(AppointmentsStates.choosing_appointment)

@router.callback_query(AppointmentsStates.choosing_appointment, F.data != 'main_menu')
async def choosing_appointment_handler(callback: CallbackQuery, state: FSMContext):
    appointment = db_utils.get_appointment_by_id(int(callback.data))
    kb = my_appointments_kb.get_conf_cancel_kb(appointment)
    service_name = db_utils.get_service_by_appointment(appointment).name
    master = db_utils.get_master_by_appointment(appointment)
    master_name = db_utils.get_user_by_master(master).name
    text = (f"Подробности:\nПроцедура: {service_name}\nМастер: {master_name}\nДата: {appointment.start_time}\n" +
            f"Статус:{appointment.status}")
    await callback.message.edit_text(text=text, reply_markup=kb)
    await state.set_state(AppointmentsStates.pressing_button)
    await callback.answer()

@router.callback_query(AppointmentsStates.pressing_button, F.data.startswith('confirm'))
async def confirm_appointment_handler(callback: CallbackQuery, state: FSMContext):
    appointment_id = int(callback.data.split('_')[-1])
    appointment = db_utils.get_appointment_by_id(appointment_id)
    db_utils.confirm_appointment(appointment)
    user = db_utils.get_user_by_telegram_id(callback.from_user.id)
    appointments = db_utils.get_appointments_by_user(user)
    kb = my_appointments_kb.get_appointments_kb(appointments)
    await callback.message.edit_text(text='Запись подтверждена. \n\n Мои записи:', reply_markup=kb)
    await state.set_state(AppointmentsStates.choosing_appointment)
    await callback.answer()

@router.callback_query(AppointmentsStates.pressing_button, F.data.startswith('cancel'))
async def cancel_appointment_handler(callback: CallbackQuery, state: FSMContext):
    appointment_id = int(callback.data.split('_')[-1])
    appointment = db_utils.get_appointment_by_id(appointment_id)
    db_utils.cancel_appointment(appointment)
    user = db_utils.get_user_by_telegram_id(callback.from_user.id)
    appointments = db_utils.get_appointments_by_user(user)
    kb = my_appointments_kb.get_appointments_kb(appointments)
    await callback.message.edit_text(text='Запись отменена. \n\n Мои записи:', reply_markup=kb)
    await state.set_state(AppointmentsStates.choosing_appointment)
    await callback.answer()

@router.callback_query(F.data == 'back')
async def main_menu_handler(callback: CallbackQuery, state: FSMContext):
    if state:
        await state.clear()
    user = db_utils.get_user_by_telegram_id(callback.from_user.id)
    appointments = db_utils.get_appointments_by_user(user)
    kb = my_appointments_kb.get_appointments_kb(appointments)
    await callback.message.edit_text(text='Мои записи:', reply_markup=kb)
    await state.set_state(AppointmentsStates.choosing_appointment)
    await callback.answer()