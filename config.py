import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'a_very_secret_key')
    MONGO_URI = 'mongodb://localhost:27017/your_database_name'
    


