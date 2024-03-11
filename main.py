import telebot # pyTelegramBotAPI
import filters # фильтры для текста
import KeyButtons # кнопки под текстовым полем
from GPT_API.gpt import GPT_API # класс обращения к GPT
import db.database as database # База данных

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


# Уведомляем о запуске бота и записываем в логи
print("Bot is started!")
gpt.set_log("Bot is started!")


# Приветственное сообщение (/start)
@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message) -> None:
    # Регистрация пользователя
    gpt.database.register_user(message.from_user.id)
    # Отправка сообщения
    markup = KeyButtons.create_keyboard(['Настроить ответ', 'Текущие настройки'])
    bot.send_message(message.chat.id, messages.welcome, reply_markup=markup)
    

# Выбор языка и сложности (/choice)
@bot.message_handler(func=filters.choice_filter)
@bot.message_handler(commands=['choice'])
def choice_command(message: telebot.types.Message) -> None:
    # Регистрация пользователя
    gpt.database.register_user(message.from_user.id)
    # Предложение выбора языка прогарммирования
    markup = KeyButtons.create_keyboard(config.CHOICE_LANGS)
    bot.send_message(message.chat.id, messages.choice_lang, reply_markup=markup)
    bot.register_next_step_handler(message, choice_lang)

def choice_lang(message: telebot.types.Message) -> None:
    if message.text not in config.CHOICE_LANGS:
        markup = KeyButtons.create_keyboard(config.CHOICE_LANGS)
        bot.send_message(message.chat.id, messages.choice_lang, reply_markup=markup)
        bot.register_next_step_handler(message, choice_lang)
        return
    
    gpt.database.set_user_data('language', message.text, message.from_user.id)
    
    markup = KeyButtons.create_keyboard(config.DIFFICULTIES)
    bot.send_message(message.chat.id, messages.choice_level, reply_markup=markup)
    
    bot.register_next_step_handler(message, choice_level)

def choice_level(message: telebot.types.Message) -> None:
    if message.text not in config.DIFFICULTIES:
        markup = KeyButtons.create_keyboard(config.DIFFICULTIES)
        bot.send_message(message.chat.id, messages.choice_level, reply_markup=markup)
        bot.register_next_step_handler(message, choice_level)
        return
    
    gpt.database.set_user_data('level', message.text, message.from_user.id)
    bot.send_message(message.chat.id, messages.choice_done)


@bot.message_handler(func=filters.settings_filter)
@bot.message_handler(commands=['settings'])
def settings_command(message: telebot.types.Message) -> None:
    user_language = gpt.database.get_user_data('language', message.from_user.id)
    user_level = gpt.database.get_user_data('level', message.from_user.id)
    
    if user_language == '':
        user_language = 'Нету'
    if user_level == '':
        user_level = 'Нету'
    
    bot.send_message(message.chat.id, messages.settings.format(user_language, user_level))
    
    
# Список команд (/help)
@bot.message_handler(commands=['help'])
def help_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    markup = KeyButtons.create_keyboard(['Настроить ответ', 'Текущие настройки'])
    bot.send_message(message.chat.id, messages.help, reply_markup=markup)


# Контакты (/contants)
@bot.message_handler(commands=['contants'])
def help_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    markup = KeyButtons.create_keyboard(['Настроить ответ', 'Текущие настройки'])
    bot.send_message(message.chat.id, messages.contants, reply_markup=markup)
    
    
# Информация (/info)
@bot.message_handler(commands=['info'])
def help_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    markup = KeyButtons.create_keyboard(['Настроить ответ', 'Текущие настройки'])
    bot.send_message(message.chat.id, messages.info.format(
        model=config.main['model'],
        max_tokens=config.main['max-tokens'],
        bot_max_tokens=config.main['bot-max-tokens'],
        bot_role=config.main['bot-role']
    ), reply_markup=markup)


# Исходный код (/open_source)
@bot.message_handler(commands=['open_source'])
def help_command(message: telebot.types.Message) -> None:
    markup = KeyButtons.create_keyboard(['Настроить ответ', 'Текущие настройки'])
    # Отправка сообщения
    bot.send_message(message.chat.id, messages.open_source, reply_markup=markup)


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
    markup = KeyButtons.create_keyboard(['Настроить ответ', 'Текущие настройки'])
    # Проверка на последний запрос
    if not gpt.is_last_answer(message.from_user.id):
        bot.send_message(message.chat.id, messages.incorrect_stop, reply_markup=markup)
        return
    
    bot.send_message(message.chat.id, messages.correct_stop, reply_markup=markup)
    gpt.clear_history(message.from_user.id)
    

# Обработчик для остальных сообщений (текстовых)
@bot.message_handler(content_types=['text'])
def text_prompt_handler(message: telebot.types.Message) -> None:
    
    gpt.database.register_user(message.from_user.id)
    
    if gpt.database.get_user_data('language', message.from_user.id) == "" or gpt.database.get_user_data('level', message.from_user.id) == "":
        bot.send_message(message.chat.id, messages.not_choiced)
        return
    
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