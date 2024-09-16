from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from db import mongo  # Import from the new db.py to avoid circular imports

class User(UserMixin):
    def __init__(self, username, password_hash, user_id=None):
        self.username = username
        self.password_hash = password_hash
        if user_id: # User ID should be set if passed
            self.id = str(user_id)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def find_by_username(username):
        # Grabs the username doc from the DB
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return User(user_data['username'], user_data['password_hash'], user_data['_id'])
        return None # If a user is not found

    @staticmethod
    def create_user(mongo, username, password):
        # Insert a new user document into MongoDB
        password_hash = generate_password_hash(password)
        return mongo.db.users.insert_one({
            "username": username,
            "password_hash": password_hash,
            "created_at": datetime.now(datetime.timezone.utc)
        })

