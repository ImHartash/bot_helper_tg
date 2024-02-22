import telebot # pyTelegramBotAPI
# from transformers import AutoTokenizer # подсчёт токенов в сообщении
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
    config.main['bot-role-usage'],
    config.main['bot-max-tokens']
)

print("Done!")

# Приветственное сообщение (/start)
@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message) -> None:
    # Отправка сообщения
    bot.send_message(message.chat.id, messages.welcome)


# Режим отладки бота (/debug)
@bot.message_handler(commands=['debug'])
def debugmode_command(message: telebot.types.Message) -> None:
    # Проверка пользователя
    if message.from_user.id not in config.testers:
        return
    
    # Отправка 00-00-00-log.log файла
    with open(gpt.get_logs_file, '+r') as f:
        bot.send_document(message.chat.id, f)
    

# Обработчик для остальных сообщений (текстовых)
@bot.message_handler(content_types=['text'])
def text_prompt_handler(message: telebot.types.Message) -> None:
    
    # Отправка сообщения готовности
    wait_message: telebot.types.Message = bot.send_message(message.chat.id, messages.waiting)
    
    # Проверка длинны сообщения
    if gpt.count_tokens(message.text) > config.main['max-tokens']:
        # Отправка сообщения
        bot.edit_message_text(messages.tokens_limit, message.chat.id, wait_message.message_id)
        return
    
    # Отправка промпта GPT
    reply = gpt.get_reply_by_prompt(message.text)
    
    # Обработка ошибки
    if len(reply) < 4 or reply == 'error':
        bot.edit_message_text(
            messages.json_error.format(reply) if reply != 'error' else messages.json_error.format('-1'),
            message.chat.id,
            wait_message.message_id
        )
        return
    
    bot.edit_message_text(reply, message.chat.id, wait_message.message_id)
    

# Запуск бота
bot.infinity_polling()