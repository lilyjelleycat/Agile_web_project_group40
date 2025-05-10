from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Movie, Member, Review, Role, UserRole
from sqlalchemy import func
import os

# Flask app setup
app = Flask(__name__)
app.secret_key = "6d3004e6e97c22637776fa971762d915"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../movies.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Routes
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("search"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        
        new_member = Member(username=username, firstName=first_name, lastName=last_name, email=email, hashPwd=password)
        db.session.add(new_member)
        db.session.commit()
        
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        member = Member.query.filter_by(username=username).first()
        print('Login attempt:', username, password)
        print('Member found:', member)
        print('Password hash:', member.hashPwd)
        print('Password check:', check_password_hash(member.hashPwd, password))
        
        if member and check_password_hash(member.hashPwd, password):
            session["username"] = username
            flash(f'Welcome back, {username}!', 'success')
            return render_template("search.html")
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/search")
def search():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template("search.html")

@app.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "")
    if q:
        results = Movie.query.filter(Movie.primaryTitle.ilike(f"%{q}%")).limit(10).all()
        return jsonify([[m.primaryTitle, m.tconst] for m in results])
    return jsonify([])

@app.route("/movie/<tconst>", methods=["GET", "POST"])
def movie_detail(tconst):
    if "username" not in session:
        return redirect(url_for("login"))
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
        return redirect(url_for("movie_detail", tconst=tconst))

    return render_template("movie_detail.html", movie=movie, reviews=reviews, avg_rating=avg_rating)

@app.route("/visualize")
def visualize():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
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

@app.route("/see-reviews", methods=["GET", "POST"])
def see_reviews():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        review_id = request.form["review_id"]
        new_content = request.form["content"]
        new_rating = float(request.form["rating"])
        review = Review.query.filter_by(id=review_id, username=username).first()
        if review:
            review.content = new_content
            review.rating = new_rating
            db.session.commit()
        return redirect(url_for("see_reviews"))

    user_reviews = Review.query.filter_by(username=username).all()
    return render_template("see_reviews.html", reviews=user_reviews)

@app.route("/review/<int:review_id>")
def view_shared_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return "Review not found", 404
    movie = Movie.query.get(review.movie_id)
    return render_template("share_review.html", review=review, movie=movie)

@app.route("/share-reviews")
def share_reviews():
    if "username" not in session:
        return redirect(url_for("login"))
    reviews = Review.query.filter_by(username=session["username"]).all()
    return render_template("share_reviews.html", reviews=reviews)

@app.route("/test-db")
def test_db():
    count = Movie.query.count()
    return f"DB Connected! Found {count} movie(s)." if count else "DB Connected, but no movie data found."



# Run the app
if __name__ == "__main__":
    if os.path.exists("movies.db"):
        with app.app_context():
            db.create_all()
    else:
        raise RuntimeError("movies.db not found in app/ directory. Please place it there before running the app.")
    
    app.run(debug=True)
