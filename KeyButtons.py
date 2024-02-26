from telebot.types import ReplyKeyboardMarkup

def create_keyboard(buttons) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(*buttons)
    return keyboard