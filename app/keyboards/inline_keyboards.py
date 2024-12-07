from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_confirmation_keyboard(appointment_id: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Подтвердить", callback_data=f"confirm_{appointment_id}"),
        InlineKeyboardButton("Отменить", callback_data=f"cancel_{appointment_id}")
    )
    return keyboard
