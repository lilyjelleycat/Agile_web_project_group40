from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Flask app setup
app = Flask(__name__)
app.secret_key = "6d3004e6e97c22637776fa971762d915"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
print('---------------------->', 'SQLAlchemy initializing')
db = SQLAlchemy(app)
print('---------------------->', 'SQLAlchemy initialized')

from app import routes