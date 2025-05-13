from flask import Blueprint, session, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager
from app.users.forms import RegistrationForm, LoginForm
from app.movies.forms import SearchForm
from app.models import Member, UserRole, Review, AnalyticsShare, ReviewShare
from flask_login import login_required, login_user, logout_user, current_user

# Blueprint for user-related routes
users = Blueprint('users', __name__)

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

@users.route("/profile")
@login_required
def profile():
    user = Member.query.get(current_user.username)
    reviews = Review.query.filter_by(username=user.username).all()

    return render_template('profile.html', user=user, reviews=reviews)

@users.route("/search_user")
@login_required
def search_user():
    q = request.args.get("q", "").strip()
    print(f"Search query: {q}")
    users = Member.query.filter(Member.username.ilike(f"%{q}%")).all()
    usernames = [u.username for u in users if u.username != current_user.username]
    return jsonify(usernames)


@users.route("/save_shares", methods=['POST'])
@login_required
def save_shares():
    data = request.get_json()
    shares = data.get("shares", []) # Expecting a list of dictionaries with usernames and share types

    # Remove old shares
    ReviewShare.query.filter_by(owner_username=current_user.username).delete()
    AnalyticsShare.query.filter_by(owner_username=current_user.username).delete()

    # Save new selections
    for entry in shares:
        user = entry.get("username")
        if not user:
            continue
        if entry.get("review"):
            db.session.add(ReviewShare(owner_username=current_user.username, viewer_username=user))
        if entry.get("analytics"):
            db.session.add(AnalyticsShare(owner_username=current_user.username, viewer_username=user))

    db.session.commit()
    return jsonify({'message': 'Success'}), 200

@users.route("/share", methods=["GET"])
@login_required
def share():
    # Get sharing records
    review_shares = ReviewShare.query.filter_by(owner_username=current_user.username).all()
    analytics_shares = AnalyticsShare.query.filter_by(owner_username=current_user.username).all()

    # Merge sharing state
    shared_status = {}

    for r in review_shares:
        shared_status.setdefault(r.viewer_username, {})["review"] = True

    for a in analytics_shares:
        shared_status.setdefault(a.viewer_username, {})["analytics"] = True

    return render_template("share.html", shared_status=shared_status)

