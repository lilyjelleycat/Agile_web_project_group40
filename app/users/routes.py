from flask import Blueprint, session, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.users.forms import RegistrationForm, LoginForm
from app.models import Member

# Blueprint for user-related routes
users = Blueprint('users', __name__)

# Routes
@users.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        
        new_member = Member(username=username, firstName=first_name, lastName=last_name, email=email, hashPwd=password)
        db.session.add(new_member)
        db.session.commit()
        
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for("users.login"))
    return render_template("register.html", form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        member = Member.query.filter_by(username=username).first()
        
        if member and check_password_hash(member.hashPwd, password):
            session["username"] = member.username
            flash(f'Welcome back, {member.username}!', 'success')
            return render_template("search.html")
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", form=form)

@users.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main.home"))