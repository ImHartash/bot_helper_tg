main = {
    "token": "6771542653:AAGJLwrr3AoITcUBFfU7PXeMYfJiIiJwEFY", # Токен бота
    "model": "TheBloke/Mistral-7B-Instruct-v0.1-GGUF", # Модель GPT (для токенизации)
    "max-tokens": 256, # Максимальное кол-во токенов в сообщении 
    "bot-max-tokens": 2048, # Максимально генерируемое кол-во токенов GPT
    "api-url": "http://localhost:1234/v1/chat/completions", # API-адрес для взаимодействия
    "bot-role": "Профессиональный программист", # Роль помощника, ответы зависят от него ("-" чтобы отключить)
    "bot-role-usage": f"Веди себя как {0} и расскажи подробно:" # Использование роли
}

testers = [1222527524]