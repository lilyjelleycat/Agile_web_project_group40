from flask import Blueprint, render_template, redirect, url_for, session
from app.models import Movie
from flask_login import current_user
from random import sample
from app import db

## Blueprint for main routes
main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("movies.search"))

    posters = db.session.query(Movie.Poster_Link).filter(Movie.Poster_Link != None).limit(50).all()
    poster_urls = [p[0] for p in posters if p[0]]
    return render_template("index.html", posters=poster_urls)

@main.route("/test-db")
def test_db():
    count = Movie.query.count()
    return f"DB Connected! Found {count} movie(s)." if count else "DB Connected, but no movie data found."
