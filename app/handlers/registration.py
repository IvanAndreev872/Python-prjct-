from aiogram import  F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import database.db_utils as db_utils
import app.keyboards.registered_users_kb as registered_users_kb
import app.keyboards.registration_kb as registration_kb
import app.keyboards.welcome_keyboard as welcome_keyboard

router = Router()

class Registration(StatesGroup):
    writing_name = State()
    writing_email = State()
    sending_contact = State()


@router.message(F.text.lower().strip() == 'отмена')
async def cancel_handler(message: Message, state: FSMContext):
    """
    Отменяет регистрацию
    """
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.clear()
    await message.answer(text='Регистрация прекращена.', reply_markup=welcome_keyboard.get_welcome_kb(message.from_user.id))

@router.message(F.text.lower() == 'регистрация')
async def start_registration_handler(message: Message, state: FSMContext):
    if not db_utils.check_new_user(message.from_user.id):
        await message.answer(text="Вы уже зарегистрированы")
    else:
        await message.answer(text="Введите имя:",
                                      reply_markup=registration_kb.get_registration_kb())
        await state.set_state(Registration.writing_name)

@router.message(Registration.writing_name)
async def written_name_handler(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text = "Теперь введите email:")
    await state.set_state(Registration.writing_email)

@router.message(Registration.writing_email)
async def written_email_handler(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Поделится контактом', request_contact=True))
    await message.answer(text='Теперь обменяйтесь контактами с ботом:', reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Registration.sending_contact)

@router.message(F.contact, Registration.sending_contact)
async def contact_handler(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if message.contact.user_id == message.from_user.id:
        await state.update_data(phone=phone)
        user_data = await state.get_data()
        db_utils.add_new_user(message.from_user.id,
                              user_data['name'],
                              user_data['phone'],
                              user_data['email']
                              )
        await message.answer(text=f'Регистрация прошла успешно', reply_markup=registered_users_kb.get_registered_kb())
        await state.clear()
    else:
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text='Поделится контактом', request_contact=True))
        await message.answer(text='Вы прислали не свой контакт. Пришлите свой:', reply_markup=builder.as_markup(resize_keyboard=True))