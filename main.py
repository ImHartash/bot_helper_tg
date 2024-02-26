import telebot # pyTelegramBotAPI
import filters # фильтры для текста
import KeyButtons # кнопки под текстовым полем
from gpt import GPT_API # класс обращения к GPT

# Конфиги для бота
import config # Основной конфиг
import messages # Конфиг ответов бота или сообщений

# Иницилизация бота
bot = telebot.TeleBot(config.main.get("token"))
# Иницилизация GPT
gpt = GPT_API(
    config.main['api-url'],
    config.main['model'],
    config.main['bot-role'],
    config.main['bot-max-tokens']
)

print("Bot started!")
gpt.set_log("Bot started")

# Приветственное сообщение (/start)
@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    bot.send_message(message.chat.id, messages.welcome)
    
    
# Список команд (/help)
@bot.message_handler(commands=['help'])
def help_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    bot.send_message(message.chat.id, messages.help)


# Контакты (/contants)
@bot.message_handler(commands=['contants'])
def help_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    bot.send_message(message.chat.id, messages.contants)
    
    
# Информация (/info)
@bot.message_handler(commands=['info'])
def help_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    bot.send_message(message.chat.id, messages.info.format(
        model=config.main['model'],
        max_tokens=config.main['max-tokens'],
        bot_max_tokens=config.main['bot-max-tokens'],
        bot_role=config.main['bot-role']
    ))


# Исходный код (/open_source)
@bot.message_handler(commands=['open_source'])
def help_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    bot.send_message(message.chat.id, messages.open_source)


# Режим отладки бота (/debug)
@bot.message_handler(commands=['debug'])
def debugmode_command(message: telebot.types.Message) -> None:
    # Проверка пользователя
    if message.from_user.id not in config.testers:
        return
    
    # Отправка 00-00-log.log файла
    with open(gpt.get_logs_filename(), 'rb') as f:
        bot.send_document(message.chat.id, f)


# Очистка истории
@bot.message_handler(func=filters.stop_filter)
def clear_history(message: telebot.types.Message) -> None:
    # Проверка на последний запрос
    if not gpt.is_last_answer(message.from_user.id):
        bot.send_message(message.chat.id, messages.incorrect_stop)
        return
    
    bot.send_message(message.chat.id, messages.correct_stop)
    gpt.clear_history(message.from_user.id)
    

# Обработчик для остальных сообщений (текстовых)
@bot.message_handler(content_types=['text'])
def text_prompt_handler(message: telebot.types.Message) -> None:
    
    # Создание клавиатуры
    markup = KeyButtons.create_keyboard(['Продолжи объяснение', 'Завершить решение'])
    
    # Проверка
    if gpt.is_last_answer(message.from_user.id) and not filters.continue_filter(message):
        bot.send_message(message.chat.id, messages.incorrect_message)
        return
    
    # Отправка сообщения готовности
    wait_message: telebot.types.Message = bot.send_message(message.chat.id, messages.waiting)
    
    # Проверка длинны сообщения
    if gpt.count_tokens(message.text) > config.main['max-tokens']:
        # Отправка сообщения
        bot.edit_message_text(messages.tokens_limit, message.chat.id, wait_message.message_id)
        return
    
    # Отправка промпта GPT
    reply = gpt.get_reply_by_prompt(message.text, message.from_user.id)
    
    # Обработка ошибки
    if len(reply) < 4 or reply == 'error':
        bot.edit_message_text(
            messages.json_error.format(reply) if reply != 'error' else messages.json_error.format('-1'),
            message.chat.id,
            wait_message.message_id
        )
        return
    
    # Удаление старого сообщения для отправки нового (надо для клавиатуры, что-бы она была не inline. Она мне не нравиться :3)
    bot.delete_message(message.chat.id, wait_message.message_id)
    # Отправка готового сообщения от GPT
    try:
        bot.send_message(message.chat.id, reply, reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiException as e:
        gpt.set_log("Произошла ошибка при обработке: " + e + "\nОтправка сообщения без парсинга...")
        bot.send_message(message.chat.id, reply, reply_markup=markup)
    

# Запуск бота
bot.infinity_polling()