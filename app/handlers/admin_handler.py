from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

import database.db_utils as db_utils
from app.keyboards.admin_kb import get_admin_kb
from app.utils.statistic import get_stat_to_xlsx

router = Router()


class Admin(StatesGroup):
    add_master = State()
    delete_master = State()
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
    await message.answer(text="Введите id мастера",
                         reply_markup=get_admin_kb(message.from_user.id))
    await state.set_state(Admin.add_master)


@router.message(Admin.add_master)
async def written_master_id_to_add_handler(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    master_data = await  state.get_data()
    db_utils.add_new_master(master_data["id"], 10, None)
    await message.answer(text="Мастер успешно добавлен!", reply_markup=get_admin_kb(message.from_user.id))
    await state.clear()


@router.message(F.text.lower().strip() == 'удалить мастера')
async def delete_master_handler(message: Message, state: FSMContext):
    await message.answer(text="Введите id мастера",
                         reply_markup=get_admin_kb(message.from_user.id))
    await state.set_state(Admin.delete_master)


@router.message(Admin.add_master)
async def written_master_id_to_delete_handler(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    master_data = await  state.get_data()
    db_utils.delete_master(db_utils.get_master(master_data["id"]))
    await message.answer(text="Мастер успешно удален!", reply_markup=get_admin_kb(message.from_user.id))
    await state.clear()


@router.message(F.text.lower().strip() == 'удалить админа')
async def delete_admin_handler(message: Message, state: FSMContext):
    await message.answer(text="Введите id админа",
                         reply_markup=get_admin_kb(message.from_user.id))
    await state.set_state(Admin.delete_master)


@router.message(Admin.delete_admin)
async def written_master_id_to_delete_handler(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    master_data = await  state.get_data()
    db_utils.delete_admin(db_utils.get_admin(master_data["id"]))
    await message.answer(text="Админ успешно удален!", reply_markup=get_admin_kb(message.from_user.id))
    await state.clear()
