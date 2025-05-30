from flask import Blueprint, request, session, render_template, redirect, url_for, jsonify, flash
from app import db
from app.models import Movie, Review, AnalyticsShare, ReviewShare,Member
from app.movies.forms import SearchForm, AnalyticsViewerForm, EditReviewForm
from app.movies.utils import searchMovies
from flask_login import login_required, current_user

# Blueprint for movie routes
movies = Blueprint('movies', __name__)

@movies.route("/search", methods=["GET", "POST"])
@login_required
def search():
    form = SearchForm()
    posters = db.session.query(Movie.Poster_Link).filter(Movie.Poster_Link != None).limit(50).all()
    poster_urls = [p[0] for p in posters]

    if form.validate_on_submit():
        search_string = form.searchString.data
        results = searchMovies(search_string)

        if not results:
            return render_template("search.html", form=form, message="No movies found.", posters=poster_urls)
        else:
            return render_template("search_results.html", movies=results)

    return render_template("search.html", form=form, posters=poster_urls, mode="user")


@movies.route("/autocomplete")
@login_required
def autocomplete():
    q = request.args.get("q", "")
    reviewed_only = request.args.get("reviewed_only") == "1"
    username = current_user.username

    if not q:
        return jsonify([])   
    base_results = searchMovies(q)

    if reviewed_only:
        reviewed_ids = {
            r.movie_id for r in Review.query.filter_by(username=username).all()
        }
        base_results = [m for m in base_results if m.tconst in reviewed_ids]
    trimmed = base_results[:10]
    return jsonify([[m.primaryTitle, m.tconst] for m in trimmed])



@movies.route("/movie/<tconst>", methods=["GET", "POST"])
@login_required
def movie_detail(tconst):
    movie = Movie.query.filter_by(tconst=tconst).first()
    if not movie:
        return "Movie not found", 404
    
    if current_user.has_role("admin"):
        return redirect(url_for("admin.edit_movie", tconst=tconst))
    
    all_reviews = Review.query.filter_by(movie_id=tconst).all()
    visible_reviews = []

    for review in all_reviews:
        author = Member.query.get(review.username)
        if author.public_reviews or review.username == current_user.username:
            visible_reviews.append(review)
        else:
            shared = ReviewShare.query.filter_by(owner_username=review.username, viewer_username=current_user.username).first()
            if shared:
                visible_reviews.append(review)

    avg_rating = (
        round(sum(r.rating for r in all_reviews) / len(all_reviews), 2)
        if all_reviews else None
    )

    # Check if current user has already reviewed this movie
    existing_review = Review.query.filter_by(username=current_user.username, movie_id=tconst).first()

    if request.method == "POST" and not existing_review:
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

    return render_template(
        "movie_detail.html",
        movie=movie,
        reviews=visible_reviews,
        avg_rating=avg_rating,
        existing_review=existing_review
    )


@movies.route('/visualize', methods=['GET', 'POST'])
@login_required
def visualize():
    selected_user = current_user.username

    shared_with_me = AnalyticsShare.query.filter_by(viewer_username=current_user.username).all()
    allowed_usernames = [s.owner_username for s in shared_with_me]

    form = AnalyticsViewerForm()
    form.friend_username.choices = [(current_user.username, "Yourself")] + [(u, u) for u in allowed_usernames]

    if form.validate_on_submit():
        selected_user = form.friend_username.data
        if selected_user != current_user.username and selected_user not in allowed_usernames:
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
@login_required
def edit_review():

    form = EditReviewForm()
    username = current_user.username
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

    username = current_user.username

    review_shares = ReviewShare.query.filter_by(owner_username=username).all()
    analytics_shares = AnalyticsShare.query.filter_by(owner_username=username).all()

    shared_status = {}

    for r in review_shares:
        shared_status.setdefault(r.viewer_username, {})["review"] = True
    for a in analytics_shares:
        shared_status.setdefault(a.viewer_username, {})["analytics"] = True

    return render_template("share_reviews.html", shared_status=shared_status)
