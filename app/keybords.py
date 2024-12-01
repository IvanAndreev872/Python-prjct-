from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Регитсрация')]
    [KeyboardButton(text = 'Вход'), KeyboardButton(text = 'Выход')]
], resize_keyboard=True, input_field_placeholder='Выберите пункт меню')