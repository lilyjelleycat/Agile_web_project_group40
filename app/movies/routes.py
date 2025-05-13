from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify
from app import db
from app.models import Movie, Review
from app.movies.forms import SearchForm
from app.movies.utils import searchMovies
from flask_login import login_required, current_user

# Blueprint for movie routes
movies = Blueprint('movies', __name__)

# Routes
@movies.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        search_string = form.searchString.data
        results = searchMovies(search_string)
        
        if not results:
            return render_template("search.html", form=form, message="No movies found.")
        else:
            return render_template("search_results.html", movies=results)
    return render_template("search.html", form=form)

@movies.route("/autocomplete")
@login_required
def autocomplete():
    q = request.args.get("q", "")
    if q:
        results = searchMovies(q)
        return jsonify([[m.primaryTitle, m.tconst] for m in results])
    return jsonify([])

@movies.route("/movie/<tconst>", methods=["GET", "POST"])
@login_required
def movie_detail(tconst):
    movie = Movie.query.filter_by(tconst=tconst).first()
    if not movie:
        return "Movie not found", 404
    reviews = Review.query.filter_by(movie_id=tconst).all()
    avg_rating = (
        round(sum(r.rating for r in reviews) / len(reviews), 2)
        if reviews else None
    )

    if request.method == "POST":
        rating = float(request.form["rating"])
        content = request.form["content"]
        new_review = Review(
            movie_id=tconst,
            username=current_user.username,
            rating=rating,
            content=content
        )
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for("movies.movie_detail", tconst=tconst))

    return render_template("movie_detail.html", movie=movie, reviews=reviews, avg_rating=avg_rating)

@movies.route("/visualize")
@login_required
def visualize():
    username = current_user.username
    user_reviews = Review.query.filter_by(username=username).all()
    reviewed_count = len(user_reviews)
    avg_rating = round(sum(r.rating for r in user_reviews) / reviewed_count, 2) if reviewed_count else 0

    genre_data = {}
    for r in user_reviews:
        movie = Movie.query.get(r.movie_id)
        if movie and movie.genres:
            for g in movie.genres.split(","):
                genre_data[g.strip()] = genre_data.get(g.strip(), 0) + 1

    return render_template("visualize.html", reviewed_count=reviewed_count, avg_rating=avg_rating, genre_data=genre_data)

@movies.route("/see_reviews", methods=["GET", "POST"])
@login_required
def see_reviews():
    username = current_user.username

    if request.method == "POST":
        review_id = request.form["review_id"]
        new_content = request.form["content"]
        new_rating = float(request.form["rating"])
        review = Review.query.filter_by(id=review_id, username=username).first()
        if review:
            review.content = new_content
            review.rating = new_rating
            db.session.commit()
        return redirect(url_for("movies.see_reviews"))

    user_reviews = Review.query.filter_by(username=username).all()
    return render_template("see_reviews.html", reviews=user_reviews)

@movies.route("/review/<int:review_id>")
@login_required
def view_shared_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return "Review not found", 404
    movie = Movie.query.get(review.movie_id)
    return render_template("share_review.html", review=review, movie=movie)

@movies.route("/share_reviews")
@login_required
def share_reviews():
    reviews = Review.query.filter_by(username=current_user.username).all()
    return render_template("share_reviews.html", reviews=reviews)
