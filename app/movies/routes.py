from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify, flash
from app import db
from app.models import Movie, Review, AnalyticsShare, ReviewShare
from app.movies.forms import SearchForm, AnalyticsViewerForm, EditReviewForm

# Blueprint for movie routes
movies = Blueprint('movies', __name__)

@movies.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
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

@movies.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "")
    reviewed_only = request.args.get("reviewed_only") == "1"
    username = session.get("username")

    if q:
        query = Movie.query

        if reviewed_only and username:
            query = query.join(Review).filter(Review.username == username)

        query = query.filter(Movie.primaryTitle.ilike(f"%{q}%"))
        results = query.limit(10).all()
        return jsonify([[m.primaryTitle, m.tconst] for m in results])

    return jsonify([])


def searchMovies(searchString):
    titleQuery1 = Movie.query.filter(Movie.primaryTitle.ilike(f"%{searchString}%"))
    titleQuery2 = Movie.query.filter(Movie.originalTitle.ilike(f"%{searchString}%"))
    dirQuery = Movie.query.filter(Movie.Director.ilike(f"%{searchString}%"))
    star1Query = Movie.query.filter(Movie.Star1.ilike(f"%{searchString}%"))
    star2Query = Movie.query.filter(Movie.Star2.ilike(f"%{searchString}%"))
    star3Query = Movie.query.filter(Movie.Star3.ilike(f"%{searchString}%"))
    star4Query = Movie.query.filter(Movie.Star4.ilike(f"%{searchString}%"))

    return titleQuery1.union(titleQuery2).union(dirQuery).union(star1Query).union(star2Query).union(star3Query).union(star4Query).all()

@movies.route("/movie/<tconst>", methods=["GET", "POST"])
def movie_detail(tconst):
    if "username" not in session:
        return redirect(url_for("users.login"))
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
            username=session["username"],
            rating=rating,
            content=content
        )
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for("movies.movie_detail", tconst=tconst))

    return render_template("movie_detail.html", movie=movie, reviews=reviews, avg_rating=avg_rating)

@movies.route('/visualize', methods=['GET', 'POST'])
def visualize():
    if 'username' not in session:
        return redirect(url_for('users.login'))

    current_user = session['username']
    selected_user = current_user

    shared_with_me = AnalyticsShare.query.filter_by(viewer_username=current_user).all()
    allowed_usernames = [s.owner_username for s in shared_with_me]

    form = AnalyticsViewerForm()
    form.friend_username.choices = [(current_user, "Yourself")] + [(u, u) for u in allowed_usernames]

    if form.validate_on_submit():
        selected_user = form.friend_username.data
        if selected_user != current_user and selected_user not in allowed_usernames:
            flash("You don't have access to view this user's analytics.", "danger")
            return redirect(url_for('movies.visualize'))

    reviews = Review.query.filter_by(username=selected_user).all()
    reviewed_count = len(reviews)
    avg_rating = round(sum([r.rating for r in reviews]) / reviewed_count, 2) if reviewed_count else 0

    genre_counts = {}
    for r in reviews:
        if r.movie and r.movie.genres:
            for genre in r.movie.genres.split(','):
                genre = genre.strip()
                genre_counts[genre] = genre_counts.get(genre, 0) + 1

    return render_template(
        "visualize.html",
        form=form,
        reviewed_count=reviewed_count,
        avg_rating=avg_rating,
        genre_data=genre_counts,
        selected_user=selected_user
    )

@movies.route("/edit_review", methods=["GET", "POST"])
def edit_review():
    if "username" not in session:
        return redirect(url_for("users.login"))

    form = EditReviewForm()
    username = session["username"]
    review = None
    tconst = request.args.get("tconst")
    no_review_msg = None

    if form.validate_on_submit():
        review = Review.query.filter_by(id=form.review_id.data, username=username).first()
        if review:
            review.rating = int(form.rating.data)
            review.content = form.content.data
            db.session.commit()
            flash("Review updated successfully.", "success")
            return redirect(url_for("movies.edit_review"))

    elif tconst:
        review = Review.query.filter_by(username=username, movie_id=tconst).first()
        if review:
            form.review_id.data = review.id
            form.rating.data = str(review.rating)
            form.content.data = review.content
        else:
            no_review_msg = "You haven't reviewed this movie yet."

    return render_template("edit_reviews.html", form=form, review=review, no_review_msg=no_review_msg)

@movies.route("/review/<int:review_id>")
def view_shared_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return "Review not found", 404
    movie = Movie.query.get(review.movie_id)
    return render_template("share_review.html", review=review, movie=movie)

@movies.route("/share_reviews")
def share_reviews():
    if "username" not in session:
        return redirect(url_for("users.login"))

    username = session["username"]

    review_shares = ReviewShare.query.filter_by(owner_username=username).all()
    analytics_shares = AnalyticsShare.query.filter_by(owner_username=username).all()

    shared_status = {}

    for r in review_shares:
        shared_status.setdefault(r.viewer_username, {})["review"] = True
    for a in analytics_shares:
        shared_status.setdefault(a.viewer_username, {})["analytics"] = True

    return render_template("share_reviews.html", shared_status=shared_status)
