from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Flask app setup
app = Flask(__name__)
app.secret_key = "6d3004e6e97c22637776fa971762d915"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager(app)
login_manager.login_view = "users.login"
    
# Register Blueprints
from app.main.routes import main
from app.users.routes import users
from app.movies.routes import movies
from app.admin.routes import admin
from app.errors.handlers import errors

app.register_blueprint(main)
app.register_blueprint(users)  
app.register_blueprint(movies)
app.register_blueprint(admin)
app.register_blueprint(errors)
