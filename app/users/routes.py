from flask import Blueprint, session, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.users.forms import RegistrationForm, LoginForm
from app.models import Member, UserRole
from flask_login import login_required, login_user, logout_user, current_user

# Blueprint for user-related routes
users = Blueprint('users', __name__)

# Routes
@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for("movies.search"))
    
    regForm = RegistrationForm()
    
    if regForm.validate_on_submit():
        username = regForm.username.data
        first_name = regForm.first_name.data
        last_name = regForm.last_name.data
        email = regForm.email.data
        password = generate_password_hash(regForm.password.data)
        
        # Create user and assign the default role
        new_member = Member(username=username, firstName=first_name, lastName=last_name, email=email, hashPwd=password)
        db.session.add(new_member)
        
        user_role = UserRole(username=username, role='user')
        db.session.add(user_role)
        db.session.commit()
        
        flash(f'Account created for {regForm.username.data}!', 'success')
        return redirect(url_for("users.login"))
    return render_template("register.html", form=regForm)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for("movies.search"))
    
    loginForm = LoginForm()
    
    if loginForm.validate_on_submit():
        member = Member.query.filter_by(username=loginForm.username.data).first()
        if member and check_password_hash(member.hashPwd, loginForm.password.data):
            login_user(member, remember=loginForm.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {member.username}!', 'info')
            return redirect(url_for("movies.search")) if not next_page else redirect(next_page)
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", form=loginForm)

@users.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for("main.home"))