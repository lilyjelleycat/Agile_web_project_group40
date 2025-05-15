import unittest
from flask_testing import TestCase
from app import create_app, db
from app.models import User, Movie, Review
import os

class BaseTestCase(TestCase):
    def create_app(self):
        """Create and configure a test Flask application instance"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        """Set up test database and test client"""
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()

class TestUserModel(BaseTestCase):
    def test_password_hashing(self):
        """Test password hashing and verification"""
        user = User(username='test_user', email='test@example.com')
        user.set_password('test_password')
        self.assertTrue(user.check_password('test_password'))
        self.assertFalse(user.check_password('wrong_password'))

    def test_user_creation(self):
        """Test user creation and retrieval"""
        user = User(username='test_user', email='test@example.com')
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()
        
        retrieved_user = User.query.filter_by(username='test_user').first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.email, 'test@example.com')

class TestMovieModel(BaseTestCase):
    def test_movie_creation(self):
        """Test movie creation and retrieval"""
        movie = Movie(
            title='Test Movie',
            description='Test Description',
            release_date='2024-01-01',
            rating=8.5
        )
        db.session.add(movie)
        db.session.commit()

        retrieved_movie = Movie.query.filter_by(title='Test Movie').first()
        self.assertIsNotNone(retrieved_movie)
        self.assertEqual(retrieved_movie.rating, 8.5)

class TestReviewModel(BaseTestCase):
    def test_review_creation(self):
        """Test review creation with user and movie relationship"""
        # Create test user
        user = User(username='test_user', email='test@example.com')
        user.set_password('test_password')
        db.session.add(user)

        # Create test movie
        movie = Movie(
            title='Test Movie',
            description='Test Description',
            release_date='2024-01-01',
            rating=8.5
        )
        db.session.add(movie)
        db.session.commit()

        # Create review
        review = Review(
            content='Great movie!',
            rating=5,
            user_id=user.id,
            movie_id=movie.id
        )
        db.session.add(review)
        db.session.commit()

        # Test relationships
        retrieved_review = Review.query.first()
        self.assertEqual(retrieved_review.user.username, 'test_user')
        self.assertEqual(retrieved_review.movie.title, 'Test Movie')

if __name__ == '__main__':
    unittest.main()
