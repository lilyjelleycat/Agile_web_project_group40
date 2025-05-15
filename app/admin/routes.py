from flask import Blueprint, session, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from app.admin.forms import UploadMoviesForm, FindMovieForm, EditMovieForm, AdminChangeUserPasswordForm
from app.models import Movie, Member, UserRole
from app.movies.utils import searchMovies
from app.admin.utils import process_movies_file
from app import db

# Blueprint for admin-related routes
admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in first", "info")
            return redirect(url_for('users.login', next=request.url))
        if not current_user.has_role('admin'):
            flash("You do not have permission to access this page", "danger")
            return redirect(url_for('main.home')) # 或者 movies.search
        return f(*args, **kwargs)
    return decorated_function

# Routes
@admin.route("/upload_movies", methods=["GET", "POST"])
def upload_movies():
    uploadMoviesForm = UploadMoviesForm()
    if uploadMoviesForm.validate_on_submit():
        file = uploadMoviesForm.file.data
        if file:
            # Process the uploaded file
            # Assuming the file is a CSV and you have a function to handle it
            process_movies_file(file)
            flash('Movies uploaded successfully!', 'success')
            return redirect(url_for("admin.upload_movies"))
        else:
            flash('No file selected!', 'danger')
    return render_template("upload_movies.html", form=uploadMoviesForm)

@admin.route("/find_movie", methods=["GET", "POST"])
def find_movie():
    form = FindMovieForm()
    if 'username' not in session:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        search_string = form.searchString.data
        results = searchMovies(search_string)
        
        if not results:
            return render_template("search.html", form=form, message="No movies found.")
        else:
            return render_template("search_results.html", movies=results)
    return render_template("search.html", form=form)

@admin.route("/edit_movie/<tconst>", methods=["GET", "POST"])
def edit_movie(tconst):
    editMovieForm = EditMovieForm()
    if editMovieForm.validate_on_submit():
        # Fetch the movie using tconst
        movie = Movie.query.filter_by(tconst=tconst).first()
        if movie:
            # Update the movie details
            movie.primaryTitle = editMovieForm.primaryTitle.data
            movie.originalTitle = editMovieForm.originalTitle.data
            movie.Poster_Link = editMovieForm.Poster_Link.data
            movie.startYear = editMovieForm.startYear.data
            movie.genres = editMovieForm.genres.data
            movie.Certificate = editMovieForm.Certificate.data
            movie.runtimeMinutes = editMovieForm.runtimeMinutes.data
            movie.Director = editMovieForm.Director.data
            movie.Star1 = editMovieForm.Star1.data
            movie.Star2 = editMovieForm.Star2.data
            movie.Star3 = editMovieForm.Star3.data
            movie.Star4 = editMovieForm.Star4.data
            movie.Overview = editMovieForm.Overview.data
            
            # Commit the changes to the database
            db.session.commit()
            flash('Movie updated successfully!', 'success')
        else:
            flash('Movie not found!', 'danger')
        return redirect(url_for("admin.find_movie"))
    
    # Fetch the movie details using tconst
    movie = Movie.query.filter_by(tconst=tconst).first()
    editMovieForm.setMovieData(movie)
    return render_template("edit_movie.html", form=editMovieForm)


# --- Administrator Dashboard Route ---
@admin.route("/dashboard")
@login_required
@admin_required
def dashboard():
    users = Member.query.all()
    return render_template("admin/admin_dashboard.html", users=users, title="Administrator Dashboard")

# --- Administrator Change User Password Route ---
@admin.route("/change_user_password/<string:username>", methods=["GET", "POST"])
@login_required
@admin_required
def change_user_password(username):
    user_to_edit = Member.query.filter_by(username=username).first_or_404()
    form = AdminChangeUserPasswordForm() # Assuming AdminChangeUserPasswordForm is defined elsewhere

    if form.validate_on_submit():
        user_to_edit.hashPwd = generate_password_hash(form.new_password.data) # Assuming hashPwd is the attribute name
        db.session.commit()
        flash(f"User {user_to_edit.username}'s password has been updated.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template(
        "admin/admin_change_password.html",
        form=form,
        user_to_edit=user_to_edit,
        title=f"Change Password for {user_to_edit.username}"
    )

# --- Delete User Route ---
@admin.route("/delete_user/<string:username>", methods=["POST"]) # Must be a POST request
@login_required
@admin_required
def delete_user(username):
    user_to_delete = Member.query.filter_by(username=username).first_or_404()

    if user_to_delete.username == current_user.username:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.dashboard"))

    try:
        # Assuming UserRole is a model related to the user
        UserRole.query.filter_by(username=user_to_delete.username).delete()

        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f"User {user_to_delete.username} has been deleted.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user {user_to_delete.username}: {str(e)}", "danger")

    return redirect(url_for("admin.dashboard"))