import requests # парсинг ответов GPT
import datetime # для логов, узнать время
import logging # логи для файла
from transformers import AutoTokenizer # Токенизация


class GPT_API:
    # Метод иницилизации
    def __init__(self, api_url: str, model: str, bot_role: str, role_usage: str, max_tokens_bot: int,) -> None:
        # Дата
        dt = datetime.datetime.now()
        
        # Токенизация
        self.tokenizator = AutoTokenizer.from_pretrained(model)
        
        # Основные настройки
        self.url = api_url
        self.bot_role = bot_role
        self.bot_role_usage = role_usage
        self.max_tokens_bot = max_tokens_bot
        
        # Настройки логов
        self.log_file_name = f"logs/{dt.month}-{dt.year}-logs.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=self.log_file_name,
            filemode='+w'
        )
    
    # Получение ответа от GPT
    def get_reply_by_prompt(self, prompt: str) -> str:
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
                        {"role": "system", "content": self.bot_role_usage.format(self.bot_role)},
                        {"role": "user", "content": prompt}
                    ],
                    'temperature': 1,
                    'max_tokens': self.max_tokens_bot
                } 
            ) if self.bot_role != '-' else requests.post(
                url = self.url,
                headers = {"Content-Type": "application/json"},
                json = {
                    'messages': [
                        {"role": "user", "content": prompt}
                    ],
                    'temperature': 1,
                    'max_tokens': self.max_tokens_bot
                }
            )
            
            # Логгируем
            self.__set_log(f'{reply.json()['choices'][0]['message']['content']}\nStatus-code: {reply.status_code}')
            
        except Exception as e:
            print(e)
            return 'error'
        
        # Обработка ошибки GPT
        if reply.status_code != 200 or 'choices' not in reply.json():
            return f'{reply.status_code}'
        
        return reply.json()['choices'][0]['message']['content']
    
    
    # Подсчет токенв в сообщении
    def count_tokens(self, message: str) -> int:
        '''
            Возвращает число токенов в сообщении
        '''
        return len(self.tokenizator.decode(message))
    
    
    # Логгирование
    def __set_log(self, log: object) -> None:
        '''
            log - текст вставляемый в логи
        '''      
        logging.info(log)
    
    # Отправляет логи
    def get_logs_file(self) -> str:
        '''
            Возвращает название файла с логгами
        '''
        return self.log_file_name