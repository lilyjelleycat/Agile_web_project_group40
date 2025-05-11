from flask import Blueprint, render_template, redirect, url_for, session
from app import app, db
from app.models import Movie

## Blueprint for main routes
main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    print('In home route')
    return render_template("index.html")
    # if "username" in session:
    #     return redirect(url_for("movies.search"))
    # print('Not logged in, redirecting to index.html')
    # return render_template("index.html")

@main.route("/test-db")
def test_db():
    count = Movie.query.count()
    return f"DB Connected! Found {count} movie(s)." if count else "DB Connected, but no movie data found."
