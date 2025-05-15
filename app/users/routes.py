from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from app import db
from app.users.forms import (
    RegistrationForm,
    LoginForm,
    ChangePasswordForm,
    ResetPasswordForm,
)
from app.movies.forms import SearchForm
from app.models import Member, UserRole, Review, AnalyticsShare, ReviewShare

# Blueprint for user-related routes
users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in!", "info")
        return redirect(url_for("movies.search"))

    regForm = RegistrationForm()
    if regForm.validate_on_submit():
        new_member = Member(
            username=regForm.username.data,
            firstName=regForm.first_name.data,
            lastName=regForm.last_name.data,
            email=regForm.email.data,
            hashPwd=generate_password_hash(regForm.password.data),
        )
        db.session.add(new_member)
        db.session.add(UserRole(username=new_member.username, role="user"))
        db.session.commit()
        flash(f"Account created for {regForm.username.data}!", "success")
        return redirect(url_for("users.login"))

    return render_template("register.html", form=regForm)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in!", "info")
        return redirect(url_for("movies.search"))

    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        member = Member.query.filter_by(username=loginForm.username.data).first()
        if member and check_password_hash(member.hashPwd, loginForm.password.data):
            login_user(member, remember=loginForm.remember.data)
            flash(f"Welcome back, {member.username}!", "info")
            next_page = request.args.get("next")
            return (
                redirect(next_page) if next_page else redirect(url_for("movies.search"))
            )
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")

    return render_template("login.html", form=loginForm)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", "info")
    return redirect(url_for("main.home"))


@users.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if current_user.is_authenticated:
        changeForm = ChangePasswordForm()
        if changeForm.validate_on_submit():
            member = Member.query.filter_by(username=current_user.username).first()
            if member and check_password_hash(
                member.hashPwd, changeForm.current_password.data
            ):
                member.hashPwd = generate_password_hash(changeForm.new_password.data)
                db.session.commit()
                logout_user()
                flash("Your password has been updated!", "success")
                return redirect(url_for("users.login"))
            else:
                flash("Current password is incorrect", "danger")
        return render_template("change_user_password.html", form=changeForm)
    else:
        flash("You need to be logged in to change your password!", "info")
        return redirect(url_for("users.login"))


@users.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    resetPasswordForm = ResetPasswordForm()
    if resetPasswordForm.validate_on_submit():
        member = Member.query.filter_by(
            username=resetPasswordForm.username.data
        ).first()
        if (
            member
            and resetPasswordForm.email.data == member.email
            and resetPasswordForm.first_name.data == member.firstName
            and resetPasswordForm.last_name.data == member.lastName
        ):
            member.hashPwd = generate_password_hash(resetPasswordForm.new_password.data)
            db.session.commit()
            flash("Your password has been reset!", "success")
            return redirect(url_for("users.login"))
        else:
            flash("Invalid username or email", "danger")

    return render_template("reset_user_password.html", form=resetPasswordForm)


@users.route("/profile")
@login_required
def profile():
    user = Member.query.get(current_user.username)
    reviews = Review.query.filter_by(username=user.username).all()
    return render_template("profile.html", user=user, reviews=reviews)


@users.route("/profile/toggle_public", methods=["POST"])
@login_required
def toggle_public():
    data = request.get_json()
    current_user.public_reviews = data.get("public", False)
    db.session.commit()
    return jsonify({"status": "success"})


@users.route("/search_user")
@login_required
def search_user():
    q = request.args.get("q", "").strip()
    users = Member.query.filter(Member.username.ilike(f"%{q}%")).all()
    usernames = [u.username for u in users if u.username != current_user.username]
    return jsonify(usernames)


@users.route("/save_shares", methods=["POST"])
@login_required
def save_shares():
    data = request.get_json()
    shares = data.get("shares", [])

    ReviewShare.query.filter_by(owner_username=current_user.username).delete()
    AnalyticsShare.query.filter_by(owner_username=current_user.username).delete()

    for entry in shares:
        user = entry.get("username")
        if not user:
            continue
        if entry.get("review"):
            db.session.add(
                ReviewShare(owner_username=current_user.username, viewer_username=user)
            )
        if entry.get("analytics"):
            db.session.add(
                AnalyticsShare(
                    owner_username=current_user.username, viewer_username=user
                )
            )

    db.session.commit()
    return jsonify({"message": "Success"}), 200


@users.route("/share", methods=["GET"])
@login_required
def share():
    review_shares = ReviewShare.query.filter_by(
        owner_username=current_user.username
    ).all()
    analytics_shares = AnalyticsShare.query.filter_by(
        owner_username=current_user.username
    ).all()

    shared_status = {}
    for r in review_shares:
        shared_status.setdefault(r.viewer_username, {})["review"] = True
    for a in analytics_shares:
        shared_status.setdefault(a.viewer_username, {})["analytics"] = True

    return render_template("share.html", shared_status=shared_status)
