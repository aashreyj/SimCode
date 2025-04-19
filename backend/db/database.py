# db/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "synccode"),
                user=os.getenv("DB_USER", "synccode_user"),
                password=os.getenv("DB_PASSWORD", "mypassword"),
                port=os.getenv("DB_PORT", 5432)
            )
            cls._instance.conn.autocommit = False
        return cls._instance
    
    def get_connection(self):
        return self.conn
    
    def get_cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)
    
    def close_connection(self):
        if self.conn:
            self.conn.close()
            
    def commit(self):
        self.conn.commit()
            
    def rollback(self):
        self.conn.rollback()