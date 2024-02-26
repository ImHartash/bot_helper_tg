class UserHistory:
    def __init__(self) -> None:
        self.users_history = {} # Создаем пустой словарь для дальнего его наполнения
    
    # Регистрация пользователя
    def register_user(self, user_id: int) -> None:
        self.users_history[str(user_id)] = {
            'last_answer': ''
        }
    
    # Установка последнего запроса
    def set_last_answer(self, user_id: int, answer: str) -> None:
        if str(user_id) not in self.users_history:
            self.register_user(user_id)
            
        self.users_history[str(user_id)]['last_answer'] += answer
    
    
    # Очистка последнего запроса
    def clear_last_answer(self, user_id: int) -> None:
        if str(user_id) not in self.users_history:
            self.register_user(user_id)
            return
            
        self.users_history[str(user_id)]['last_answer'] = ""
    
        
    # Получение последнего запроса
    def get_last_answer(self, user_id: int) -> str:
        if str(user_id) not in self.users_history:
            self.register_user(user_id)
        
        return self.users_history[str(user_id)]['last_answer']