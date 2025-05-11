from flask import Blueprint, session, render_template, redirect, url_for, flash
from app.admin.forms import UploadMoviesForm, FindMovieForm, EditMovieForm
from app.models import Movie
from app.movies.utils import searchMovies
from app.admin.utils import process_movies_file
from app import db

# Blueprint for admin-related routes
admin = Blueprint('admin', __name__)

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