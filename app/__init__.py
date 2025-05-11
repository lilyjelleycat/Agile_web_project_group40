from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

# Flask app setup
app = Flask(__name__)
app.secret_key = "6d3004e6e97c22637776fa971762d915"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Register Blueprints
from app.main.routes import main
from app.users.routes import users
from app.movies.routes import movies

app.register_blueprint(main)
from app.users.routes import users
app.register_blueprint(users, url_prefix="/users")
app.register_blueprint(movies)