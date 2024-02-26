from telebot.types import Message

def stop_filter(message: Message) -> bool:
    return message.text == "Завершить решение"

def continue_filter(message: Message) -> bool:
    return message.text == "Продолжи объяснение"