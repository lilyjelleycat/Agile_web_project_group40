import pytest
from app import create_app, db
from app.models import User, Movie, Review

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    
    # Create the database and the database tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_movie(app):
    """Create a test movie."""
    with app.app_context():
        movie = Movie(
            title='Test Movie',
            description='Test Description',
            release_year=2023,
            genre='Action'
        )
        db.session.add(movie)
        db.session.commit()
        return movie

@pytest.fixture
def test_review(app, test_user, test_movie):
    """Create a test review."""
    with app.app_context():
        review = Review(
            content='Great movie!',
            rating=5,
            user_id=test_user.id,
            movie_id=test_movie.id
        )
        db.session.add(review)
        db.session.commit()
        return review 