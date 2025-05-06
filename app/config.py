import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = 'sqllite:///' + os.path.join(basedir, 'movies.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or default_db_path
    SECRET_KEY = '1fc8c767c862b0b854db2b2f1bd9eb28'