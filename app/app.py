from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Movie, Member, Review, Role, UserRole
from sqlalchemy import func
import os

# Flask app setup
app = Flask(__name__)
app.secret_key = "6d3004e6e97c22637776fa971762d915"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Routes
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("search"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    print('Register route accessed')
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = generate_password_hash(form.password.data)

        #new_member = Member(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        #db.session.add(new_member)
        #db.session.commit()

        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


# Run the app
if __name__ == "__main__":
    if os.path.exists("movies.db"):
        with app.app_context():
            db.create_all()
    else:
        raise RuntimeError("movies.db not found in app/ directory. Please place it there before running the app.")
    
    app.run(debug=True)
