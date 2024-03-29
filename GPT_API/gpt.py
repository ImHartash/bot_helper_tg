import requests # парсинг ответов GPT
import datetime # для логов, узнать время
import logging # логи для файла # история запросов к GPT
from transformers import AutoTokenizer # Токенизация
from db.database import Database


class GPT_API:
    # Метод иницилизации
    def __init__(self, api_url: str, model: str, bot_role: str, max_tokens_bot: int,) -> None:
        # Дата
        dt = datetime.datetime.now()
        
        # Токенизация
        self.tokenizator = None
        if model != "-":
            self.tokenizator = AutoTokenizer.from_pretrained(model)
            
        # БД
        self.database = Database()
        
        # Основные настройки
        self.url = api_url
        self.bot_role = bot_role
        self.max_tokens_bot = max_tokens_bot
        
        # Иницилизация историй
        self.assistant_data = "Решим задачу по шагам: "
        
        # Настройки логов
        correct_data = self.__correct_data(dt.month, dt.year)
        
        self.log_file_name = f"logs/{correct_data[0]}-{correct_data[1]}-logs.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=self.log_file_name,
            filemode='+w'
        )
    
    # Получение ответа от GPT
    def get_reply_by_prompt(self, prompt: str, user_id: int) -> str:
        '''
            prompt - вопрос/сообщение для GPT
            
            Возвращает ответ на промпт
        '''
        try:
            
            # Отправка и получение ответа от сервера
            reply = requests.post(
                url = self.url,
                headers = {"Content-Type": "application/json"},
                json = {
                    'messages': [
                        {"role": "system", "content": self.bot_role.format(self.database.get_user_data('language', user_id), 
                                                                           self.database.get_user_data('level', user_id))},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": self.assistant_data + self.database.get_user_data('gpt_history', user_id)}
                    ],
                    'temperature': 1,
                    'max_tokens': self.max_tokens_bot
                } 
            ) if self.bot_role != '-' else requests.post(
                url = self.url,
                headers = {"Content-Type": "application/json"},
                json = {
                    'messages': [
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": self.assistant_data + self.database.get_user_data('gpt_history', user_id)}
                    ],
                    'temperature': 1,
                    'max_tokens': self.max_tokens_bot
                }
            )
            
            # Логгируем
            self.set_log(f"{reply.json()['choices'][0]['message']['content']}\nStatus-code: {reply.status_code}")
            self.database.set_user_data('user_history', prompt, user_id)
            
            # Записываем последний результат
            self.database.set_user_data('gpt_history', 
                                        self.database.get_user_data('gpt_history', user_id) + reply.json()['choices'][0]['message']['content'],
                                        user_id)
        
        except Exception as e:
            self.set_log(f'{reply.json()}\nStatus-code: {e}')
            return 'error'
        
        # Обработка ошибки GPT
        if reply.status_code != 200 or 'choices' not in reply.json():
            return f'{reply.status_code}'
        
        return reply.json()['choices'][0]['message']['content']

    
    # Очистка истории (для соединения с user_history)
    def clear_history(self, user_id: int) -> None:
        '''
            Очищает историю запросов.
        '''
        self.database.set_user_data('gpt_history', '', user_id)
        self.database.set_user_data('user_history', '', user_id)
    
    
    # Для проверки на последний запрос
    def is_last_answer(self, user_id: int) -> bool:
        return self.database.get_user_data('gpt_history', user_id)
    
    
    # Подсчет токенв в сообщении
    def count_tokens(self, message: str) -> int:
        '''
            Возвращает число токенов в сообщении
        '''
        if self.tokenizator != None:
            return len(self.tokenizator.decode(message))
        
        return len(message)
    
    
    # Логгирование
    def set_log(self, log: object) -> None:
        '''
            log - текст вставляемый в логи
        '''      
        logging.info(log)
        
    # Правильное расположение даты (Только для логов)
    def __correct_data(self, month, year) -> list:
        if month < 10:
            correct_month = "0" + str(month)
        else:
            correct_month = str(month)
        
        correct_year = str(year)[2:]
        
        return [correct_month, correct_year]
    
    # Установка языка программирования
    def set_language(self, user_id: int, lang: str) -> None:
        if not self.database.is_user_register(user_id):
            self.database.register_user(user_id)
        
        self.database.set_user_data('language', lang, user_id)
    
    # Установка уровня объяснения
    def set_level(self, user_id: int, level: str) -> None:
        if not self.database.is_user_register(user_id):
            self.database.register_user(user_id)
        
        self.database.set_user_data('level', level, user_id)
    
    # Отправляет логи
    def get_logs_filename(self) -> str:
        '''
            Возвращает название файла с логами
        '''
        return self.log_file_name