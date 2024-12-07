from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_master_appointments_keyboard(appointment_id: int) -> InlineKeyboardMarkup:
    """
    Генерация клавиатуры для управления записями мастера.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Уведомить клиента", callback_data=f"notify_{appointment_id}"
                ),
                InlineKeyboardButton(
                    text="Изменить запись", callback_data=f"edit_{appointment_id}"
                ),
            ]
        ]
    )
