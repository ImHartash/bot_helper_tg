import sqlite3

class Database:
    def __init__(self, file_name: str = "database.db", add_if_not_exists: bool = True) -> None:
        self.file_name = file_name
        
        if add_if_not_exists:
            self.__create_database()
    
    
    def __create_database(self) -> None:
        connector = sqlite3.connect(self.file_name)
        cursor = connector.cursor()
        
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
        
        cursor.execute(request)
        connector.commit()
        
    
    def set_user_data(self, data_name: str, data: str, user_id: int) -> None:
        connector = sqlite3.connect(self.file_name)
        cursor = connector.cursor()
        
        request = f'''
        UPDATE users_data
        SET {data_name} = ?
        WHERE user_id = ?;
        '''
        
        cursor.execute(request, (data, user_id))
        connector.commit()
        
        connector.close()
    
    
    def get_user_data(self, data_name: str, user_id: int) -> str:
        connector = sqlite3.connect(self.file_name)
        cursor = connector.cursor()
        
        request = f'''
        SELECT {data_name} FROM users_data WHERE user_id = {user_id};
        '''
        
        result = cursor.execute(request).fetchone()
        connector.close()
        
        return result[0]
    
    
    def is_user_register(self, user_id: int) -> bool:
        connector = sqlite3.connect(self.file_name)
        cursor = connector.cursor()
        
        request = f'''
        SELECT * FROM users_data 
        WHERE user_id = {user_id};
        '''
        
        rows = cursor.execute(request)
        is_registered = not rows.fetchone() is None
        connector.close()
        
        return is_registered
    
    
    def register_user(self, user_id: int) -> None:
        connector = sqlite3.connect(self.file_name)
        cursor = connector.cursor()
        
        if self.is_user_register(user_id):
            return
        
        request = f'''
        INSERT INTO users_data(user_id, language, level, user_history, gpt_history)
        VALUES ({user_id}, "", "", "", "");
        '''
        
        cursor.execute(request)
        connector.commit()