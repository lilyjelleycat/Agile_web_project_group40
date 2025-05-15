from test import BaseTestCase
from app.models import User, Movie, Review
from app import db
import json

class TestAuthRoutes(BaseTestCase):
    def test_register(self):
        """Test user registration"""
        response = self.client.post('/auth/register', data={
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'test_password',
            'password2': 'test_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='new_user').first()
        self.assertIsNotNone(user)

    def test_login_logout(self):
        """Test login and logout functionality"""
        # Create a test user
        user = User(username='test_user', email='test@example.com')
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()

        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'test_user',
            'password': 'test_password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

class TestMovieRoutes(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create test user and log them in
        self.user = User(username='test_user', email='test@example.com')
        self.user.set_password('test_password')
        db.session.add(self.user)
        db.session.commit()
        self.client.post('/auth/login', data={
            'username': 'test_user',
            'password': 'test_password'
        })

    def test_movie_creation(self):
        """Test movie creation route"""
        response = self.client.post('/movies/create', data={
            'title': 'New Movie',
            'description': 'Test Description',
            'release_date': '2024-01-01',
            'rating': 8.5
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        movie = Movie.query.filter_by(title='New Movie').first()
        self.assertIsNotNone(movie)

    def test_movie_list(self):
        """Test movie listing route"""
        # Create some test movies
        movie1 = Movie(title='Movie 1', description='Desc 1', release_date='2024-01-01', rating=8.5)
        movie2 = Movie(title='Movie 2', description='Desc 2', release_date='2024-01-02', rating=7.5)
        db.session.add_all([movie1, movie2])
        db.session.commit()

        response = self.client.get('/movies/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Movie 1', response.data)
        self.assertIn(b'Movie 2', response.data)

class TestReviewRoutes(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Create test user and movie
        self.user = User(username='test_user', email='test@example.com')
        self.user.set_password('test_password')
        db.session.add(self.user)
        
        self.movie = Movie(
            title='Test Movie',
            description='Test Description',
            release_date='2024-01-01',
            rating=8.5
        )
        db.session.add(self.movie)
        db.session.commit()

        # Log in the user
        self.client.post('/auth/login', data={
            'username': 'test_user',
            'password': 'test_password'
        })

    def test_create_review(self):
        """Test review creation"""
        response = self.client.post(f'/movies/{self.movie.id}/review', data={
            'content': 'Great movie!',
            'rating': 5
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        review = Review.query.filter_by(movie_id=self.movie.id).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.content, 'Great movie!')
        self.assertEqual(review.rating, 5)

if __name__ == '__main__':
    unittest.main() 