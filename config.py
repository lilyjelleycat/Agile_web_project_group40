import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_db_path = 'sqllite:///' + os.path.join(basedir, 'movies.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or default_db_path
    SECRET_KEY = 'amber_pearl_latte_is_the_best'