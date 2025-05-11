from flask import Blueprint, session, render_template, redirect, url_for, flash,request,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.users.forms import RegistrationForm, LoginForm
from app.movies.forms import SearchForm
from app.models import Member, UserRole,Review,AnalyticsShare,ReviewShare

# Blueprint for user-related routes
users = Blueprint('users', __name__)

# Routes
@users.route("/register", methods=["GET", "POST"])
def register():
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
    loginForm = LoginForm()
    
    if loginForm.validate_on_submit():
        username = loginForm.username.data
        password = loginForm.password.data
        
        member = Member.query.filter_by(username=username).first()
        
        if member and check_password_hash(member.hashPwd, password):
            session["username"] = member.username
            flash(f'Welcome back, {member.username}!', 'success')
            return redirect(url_for("movies.search"))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html", form=loginForm)

@users.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("main.home"))

@users.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('users.login'))

    user = Member.query.get(session['username'])
    reviews = Review.query.filter_by(username=user.username).all()

    return render_template('profile.html', user=user, reviews=reviews)

@users.route('/search_user')
def search_user():
    q = request.args.get("q", "").strip()
    print(f"QUERY: {q}")  # ← Add this
    if 'username' not in session or not q:
        return jsonify([])

    current_user = session['username']
    users = Member.query.filter(Member.username.ilike(f"%{q}%")).all()
    usernames = [u.username for u in users if u.username != current_user]
    print(f"FOUND USERS: {usernames}")  # ← Add this too
    return jsonify(usernames)

@users.route('/save_shares', methods=['POST'])
def save_shares():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    current_user = session['username']
    shares = data.get("shares", [])  # Format: [{username: 'alex', review: true, analytics: false}]

    # Clear old shares
    ReviewShare.query.filter_by(owner_username=current_user).delete()
    AnalyticsShare.query.filter_by(owner_username=current_user).delete()

    # Save new selections
    for entry in shares:
        user = entry.get("username")
        if not user:
            continue
        if entry.get("review"):
            db.session.add(ReviewShare(owner_username=current_user, viewer_username=user))
        if entry.get("analytics"):
            db.session.add(AnalyticsShare(owner_username=current_user, viewer_username=user))

    db.session.commit()
    return jsonify({'message': 'Success'}), 200
