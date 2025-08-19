# keyboards/inline.py

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_tc_keyboard(user_id: int):
    buttons = [
        [InlineKeyboardButton(text="✅ I Accept the T&C", callback_data=f"user_accept:{user_id}")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard