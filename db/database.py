import sqlite3

class Database:
    def __init__(self, file_name: str = "database.db", add_if_not_exists: bool = True) -> None:
        self.connector = sqlite3.connect(file_name)
        self.cursor = self.connector.cursor()
        
        if add_if_not_exists:
            self.__create_database(file_name)
    
    
    def __create_database(self, db_name: str) -> None:
        request = '''
        CREATE TABLE IF NOT EXISTS users_data(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            language TEXT,
            level TEXT,
            user_history TEXT,
            gpt_history TEXT
        );
        '''
        
        self.cursor.execute(request)
        self.connector.commit()
        
    
    def set_user_data(self, data_name: str, data: str, user_id: int) -> None:
        request = f'''
        UPDATE users_data
        SET {data_name} = {data}
        WHERE user_id = {user_id};
        '''
        
        self.cursor.execute(request)
        self.connector.commit()
    
    
    def is_user_register(self, user_id: int) -> bool:
        request = f'''
        SELECT * FROM users_data 
        WHERE user_id = {user_id};
        '''
        
        return len(request) > 0
    
    
    def register_user(self, user_id: int) -> None:
        if self.is_user_register(user_id):
            return
        
        request = f'''
        INSERT INTO users_data(user_id, language, level, user_history, gpt_history)
        VALUES ({user_id}, NULL, NULL, "", "");
        '''
        
        self.cursor.execute(request)
        self.connector.commit()
    
    
    def close_connection(self) -> None:
        self.connector.close()