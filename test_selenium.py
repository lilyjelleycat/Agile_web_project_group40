import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from app.models import User, Movie
import threading
import time

class TestSeleniumBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up Flask application
        cls.app = create_app()
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Set up database
        db.create_all()
        
        # Start Flask server in a separate thread
        cls.server_thread = threading.Thread(target=cls.app.run, kwargs={
            'port': 5000,
            'use_reloader': False
        })
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Give the server time to start

        # Set up WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        cls.driver.implicitly_wait(10)
        cls.base_url = 'http://localhost:5000'

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        db.create_all()
        self.create_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_test_data(self):
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

class TestAuthentication(TestSeleniumBase):
    def test_registration_flow(self):
        """Test user registration through the web interface"""
        self.driver.get(f"{self.base_url}/auth/register")
        
        # Fill in registration form
        self.driver.find_element(By.NAME, "username").send_keys("new_user")
        self.driver.find_element(By.NAME, "email").send_keys("new_user@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("test_password")
        self.driver.find_element(By.NAME, "password2").send_keys("test_password")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Check if registration was successful
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Verify user was created in database
        user = User.query.filter_by(username="new_user").first()
        self.assertIsNotNone(user)

    def test_login_flow(self):
        """Test user login through the web interface"""
        self.driver.get(f"{self.base_url}/auth/login")
        
        # Fill in login form
        self.driver.find_element(By.NAME, "username").send_keys("test_user")
        self.driver.find_element(By.NAME, "password").send_keys("test_password")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Check if login was successful
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )

class TestMovieInterface(TestSeleniumBase):
    def test_movie_creation_flow(self):
        """Test movie creation through the web interface"""
        # Login first
        self.driver.get(f"{self.base_url}/auth/login")
        self.driver.find_element(By.NAME, "username").send_keys("test_user")
        self.driver.find_element(By.NAME, "password").send_keys("test_password")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Navigate to movie creation page
        self.driver.get(f"{self.base_url}/movies/create")
        
        # Fill in movie creation form
        self.driver.find_element(By.NAME, "title").send_keys("New Selenium Movie")
        self.driver.find_element(By.NAME, "description").send_keys("Created via Selenium")
        self.driver.find_element(By.NAME, "release_date").send_keys("2024-01-01")
        self.driver.find_element(By.NAME, "rating").send_keys("8.5")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Check if movie was created
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Verify movie was created in database
        movie = Movie.query.filter_by(title="New Selenium Movie").first()
        self.assertIsNotNone(movie)

    def test_movie_listing_page(self):
        """Test movie listing page functionality"""
        # Login first
        self.driver.get(f"{self.base_url}/auth/login")
        self.driver.find_element(By.NAME, "username").send_keys("test_user")
        self.driver.find_element(By.NAME, "password").send_keys("test_password")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Navigate to movie listing page
        self.driver.get(f"{self.base_url}/movies/")
        
        # Check if test movie is displayed
        movie_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Test Movie')]"))
        )
        self.assertIsNotNone(movie_element)

class TestReviewInterface(TestSeleniumBase):
    def test_review_creation_flow(self):
        """Test review creation through the web interface"""
        # Login first
        self.driver.get(f"{self.base_url}/auth/login")
        self.driver.find_element(By.NAME, "username").send_keys("test_user")
        self.driver.find_element(By.NAME, "password").send_keys("test_password")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Navigate to movie detail page
        movie = Movie.query.first()
        self.driver.get(f"{self.base_url}/movies/{movie.id}")
        
        # Fill in review form
        self.driver.find_element(By.NAME, "content").send_keys("Great movie! Selenium test review.")
        self.driver.find_element(By.NAME, "rating").send_keys("5")
        self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

        # Check if review was created
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        
        # Verify review appears on page
        review_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Selenium test review')]")
        self.assertIsNotNone(review_element)

if __name__ == '__main__':
    unittest.main() 