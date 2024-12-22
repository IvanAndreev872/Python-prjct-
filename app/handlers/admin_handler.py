from aiogram import F, Router
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

import database.db_utils as db_utils
from app.keyboards.admin_kb import get_admin_kb
from app.utils.statistic import get_stat_to_xlsx

router = Router()


class Admin(StatesGroup):
    add_master_contact = State()
    add_master_services = State()
    add_master_experience = State()
    delete_master = State()
    delete_admin = State()
    add_admin = State()


@router.message(F.text.lower().strip() == 'консоль админа')
async def admin_start_handler(message: Message):
    kb = get_admin_kb(message.from_user.id)
    await message.answer(f"Функции админа!", reply_markup=kb)


@router.message(F.text.lower().strip() == 'статистика')
async def stat_handler(message: Message, state: FSMContext):
    get_stat_to_xlsx()
    with open("../../files/stat.xlsx", "rb") as file:
        await message.reply_document(document=file, filename="stat.xlsx")
    await message.answer(text='Статистика отправлена', reply_markup=get_admin_kb(message.from_user.id))


@router.message(F.text.lower().strip() == 'добавить мастера')
async def add_master_handler(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Поделиться контактом', request_contact=True))
    await message.answer(text='Отправьте контакт мастера:', reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Admin.add_master_contact)


@router.message(Admin.add_master_contact)
async def received_master_contact(message: Message, state: FSMContext):
    master_id = message.contact.user_id

    await state.update_data(master_id=master_id)

    await message.answer(text="Введите предоставляемые услуги мастера:")
    await state.set_state(Admin.add_master_services)


@router.message(Admin.add_master_services)
async def received_master_services(message: Message, state: FSMContext):
    services = message.text.strip()
    await state.update_data(services=services)

    await message.answer(text="Введите опыт работы мастера (например, количество лет):")
    await state.set_state(Admin.add_master_experience)


@router.message(Admin.add_master_experience)
async def received_master_experience(message: Message, state: FSMContext):
    experience = message.text.strip()

    master_data = await state.get_data()
    master_id = master_data["master_id"]
    services = master_data["services"]

    db_utils.add_new_master(master_id, experience, services)

    await message.answer(text="Мастер успешно добавлен!", reply_markup=get_admin_kb(message.from_user.id))
    await state.clear()

@router.message(F.text.lower().strip() == 'удалить мастера')
async def delete_master_handler(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Поделиться контактом', request_contact=True))
    await message.answer(text='Отправьте контакт, чтобы удалить мастера:',
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Admin.delete_master)


@router.message(Admin.delete_master)
async def written_master_id_to_delete_handler(message: Message, state: FSMContext):
    user_id = message.contact.user_id

    if not db_utils.is_master(user_id):
        await message.answer(text="Этот пользователь не является мастером.")
        await state.clear()
        return

    db_utils.delete_master(user_id)
    await message.answer(text="Админ успешно удален!", reply_markup=get_admin_kb(message.from_user.id))
    await state.clear()

@router.message(F.text.lower().strip() == 'добавить админа')
async def add_admin_handler(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Поделиться контактом', request_contact=True))
    await message.answer(text='Отправьте контакт мастера:', reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Admin.add_admin)

@router.message(Admin.add_admin)
async def received_master_contact(message: Message, state: FSMContext):
    admin_id = message.contact.user_id

    db_utils.add_new_admin(admin_id)

    await message.answer(text="Админ успешно добавлен!", reply_markup=get_admin_kb(message.from_user.id))
    await state.clear()

@router.message(F.text.lower().strip() == 'удалить админа')
async def delete_admin_handler(message: Message, state: FSMContext):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Поделиться контактом', request_contact=True))
    await message.answer(text='Отправьте контакт, чтобы удалить админа:',
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Admin.delete_admin)


@router.message(Admin.delete_admin)
async def written_admin_id_to_delete_handler(message: Message, state: FSMContext):
    user_id = message.contact.user_id

    if not db_utils.is_admin(user_id):
        await message.answer(text="Этот пользователь не является администратором.")
        await state.clear()
        return

    db_utils.delete_admin(user_id)
    await message.answer(text="Админ успешно удален!", reply_markup=get_admin_kb(message.from_user.id))
    await state.clear()
