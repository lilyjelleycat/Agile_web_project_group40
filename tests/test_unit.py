import unittest
from app import create_app, db
from app.models import User, Movie, Review
from flask_login import current_user
from flask import url_for

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'

class UnitTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test user model creation and password hashing"""
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        retrieved_user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(retrieved_user)
        self.assertTrue(retrieved_user.check_password('password123'))
        self.assertFalse(retrieved_user.check_password('wrongpassword'))

    def test_movie_creation(self):
        """Test movie model creation and relationships"""
        movie = Movie(
            title='Test Movie',
            description='Test Description',
            release_year=2023,
            genre='Action'
        )
        db.session.add(movie)
        db.session.commit()

        retrieved_movie = Movie.query.filter_by(title='Test Movie').first()
        self.assertIsNotNone(retrieved_movie)
        self.assertEqual(retrieved_movie.release_year, 2023)

    def test_review_creation(self):
        """Test review creation and relationships"""
        user = User(username='reviewer', email='reviewer@example.com')
        movie = Movie(title='Movie to Review', release_year=2023)
        db.session.add_all([user, movie])
        db.session.commit()

        review = Review(
            content='Great movie!',
            rating=5,
            user_id=user.id,
            movie_id=movie.id
        )
        db.session.add(review)
        db.session.commit()

        retrieved_review = Review.query.first()
        self.assertIsNotNone(retrieved_review)
        self.assertEqual(retrieved_review.rating, 5)
        self.assertEqual(retrieved_review.user.username, 'reviewer')

    def test_user_registration(self):
        """Test user registration route"""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)

    def test_user_login_logout(self):
        """Test user login and logout functionality"""
        # Create test user
        user = User(username='loginuser', email='login@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'loginuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_movie_creation_route(self):
        """Test movie creation through route"""
        # Create and login as admin user
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('adminpass')
        db.session.add(admin)
        db.session.commit()

        self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'adminpass'
        })

        response = self.client.post('/movies/create', data={
            'title': 'New Movie',
            'description': 'New movie description',
            'release_year': '2023',
            'genre': 'Action'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        movie = Movie.query.filter_by(title='New Movie').first()
        self.assertIsNotNone(movie)

if __name__ == '__main__':
    unittest.main() 