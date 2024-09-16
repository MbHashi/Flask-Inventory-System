from flask_pymongo import PyMongo

# I have imported Mongo in this file to avoid circular imports between 'app,py' & 'models.py'
mongo = PyMongo()
