import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from app import create_app, db
from app.models import User, Movie
import time

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5000'

class SeleniumTests(unittest.TestCase):
    def setUp(self):
        # Set up Chrome options for testing
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Create and configure app
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Set up database
        db.create_all()
        
        # Create test user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        """Test that home page loads and contains expected elements"""
        self.driver.get('http://localhost:5000')
        
        # Check title
        self.assertIn('Cinebuff', self.driver.title)
        
        # Check navigation elements
        nav = self.driver.find_element(By.TAG_NAME, 'nav')
        self.assertIsNotNone(nav)
        
        # Check for login/register links when not logged in
        login_link = self.driver.find_element(By.LINK_TEXT, 'Login')
        self.assertIsNotNone(login_link)

    def test_user_registration(self):
        """Test user registration process"""
        self.driver.get('http://localhost:5000/auth/register')
        
        # Fill in registration form
        username_field = self.driver.find_element(By.NAME, 'username')
        email_field = self.driver.find_element(By.NAME, 'email')
        password_field = self.driver.find_element(By.NAME, 'password')
        password2_field = self.driver.find_element(By.NAME, 'password2')
        
        username_field.send_keys('newuser')
        email_field.send_keys('newuser@example.com')
        password_field.send_keys('password123')
        password2_field.send_keys('password123')
        
        # Submit form
        password2_field.send_keys(Keys.RETURN)
        
        # Wait for redirect and check success
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be('http://localhost:5000/')
        )

    def test_user_login(self):
        """Test user login process"""
        self.driver.get('http://localhost:5000/auth/login')
        
        # Fill in login form
        username_field = self.driver.find_element(By.NAME, 'username')
        password_field = self.driver.find_element(By.NAME, 'password')
        
        username_field.send_keys('testuser')
        password_field.send_keys('password123')
        
        # Submit form
        password_field.send_keys(Keys.RETURN)
        
        # Wait for redirect and check success
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be('http://localhost:5000/')
        )
        
        # Verify login success
        profile_link = self.driver.find_element(By.LINK_TEXT, 'Profile')
        self.assertIsNotNone(profile_link)

    def test_movie_search(self):
        """Test movie search functionality"""
        # Login first
        self.test_user_login()
        
        # Add test movie to database
        movie = Movie(
            title='Test Movie',
            description='Test Description',
            release_year=2023,
            genre='Action'
        )
        db.session.add(movie)
        db.session.commit()
        
        # Go to search page
        self.driver.get('http://localhost:5000/movies/search')
        
        # Perform search
        search_field = self.driver.find_element(By.NAME, 'search')
        search_field.send_keys('Test Movie')
        search_field.send_keys(Keys.RETURN)
        
        # Wait for results and verify
        movie_title = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Test Movie'))
        )
        self.assertIsNotNone(movie_title)

    def test_movie_details(self):
        """Test viewing movie details"""
        # Login first
        self.test_user_login()
        
        # Add test movie to database
        movie = Movie(
            title='Test Movie Details',
            description='Test Description',
            release_year=2023,
            genre='Action'
        )
        db.session.add(movie)
        db.session.commit()
        
        # Go to movie details page
        self.driver.get(f'http://localhost:5000/movies/{movie.id}')
        
        # Verify movie details are displayed
        title = self.driver.find_element(By.CLASS_NAME, 'movie-title')
        self.assertEqual(title.text, 'Test Movie Details')
        
        description = self.driver.find_element(By.CLASS_NAME, 'movie-description')
        self.assertEqual(description.text, 'Test Description')

    def test_add_review(self):
        """Test adding a movie review"""
        # Login first
        self.test_user_login()
        
        # Add test movie to database
        movie = Movie(
            title='Movie to Review',
            description='Test Description',
            release_year=2023,
            genre='Action'
        )
        db.session.add(movie)
        db.session.commit()
        
        # Go to movie details page
        self.driver.get(f'http://localhost:5000/movies/{movie.id}')
        
        # Fill in review form
        review_field = self.driver.find_element(By.NAME, 'content')
        rating_field = self.driver.find_element(By.NAME, 'rating')
        
        review_field.send_keys('Great movie!')
        rating_field.send_keys('5')
        
        # Submit review
        review_field.submit()
        
        # Verify review appears on page
        review_content = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'review-content'))
        )
        self.assertEqual(review_content.text, 'Great movie!')

if __name__ == '__main__':
    unittest.main() 