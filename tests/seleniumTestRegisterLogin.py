import unittest
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tests.testConf import TEST_USER, TEST_DB_URI
from app import app, db
from app.models import Member, UserRole, Role

class RegisterLoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DB_URI
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        
        # Set up Chrome options for headless browser
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # set window size
        
        # Initialize the webdriver with Chrome options
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)
        
        # use different port to avoid conflict
        cls.port = 5001
        
        # Start Flask app in a separate thread
        cls.server_thread = threading.Thread(target=lambda: app.run(port=cls.port, debug=False, use_reloader=False))
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Give the server a moment to start
        time.sleep(2)
        
        # Create database tables
        with app.app_context():
            db.create_all()
            
            # Add role if it doesn't exist
            if not Role.query.filter_by(role='user').first():
                db.session.add(Role(role='user'))
                db.session.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up resources
        cls.driver.quit()
        
        # Remove test data
        with app.app_context():
            db.drop_all()

    def setUp(self):
        # Clear database tables before each test
        with app.app_context():
            Member.query.delete()
            UserRole.query.delete()
            db.session.commit()

    def test_successful_registration(self):
        """Test user registration with valid data"""
        self.driver.get(f'http://localhost:{self.port}/register')
        
        # wait for page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        
        # Fill out the registration form
        self.driver.find_element(By.ID, 'username').send_keys(TEST_USER['username'])
        self.driver.find_element(By.ID, 'first_name').send_keys(TEST_USER['first_name'])
        self.driver.find_element(By.ID, 'last_name').send_keys(TEST_USER['last_name'])
        self.driver.find_element(By.ID, 'email').send_keys(TEST_USER['email'])
        self.driver.find_element(By.ID, 'password').send_keys(TEST_USER['password'])
        self.driver.find_element(By.ID, 'confirm_password').send_keys(TEST_USER['password'])
        
        # ensure page is loaded and submit button is visible
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
        )
        
        # use JavaScript to click button instead of direct click
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)  # wait for scroll to complete
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # check if registration is successful and redirect to login page or directly to search page
        wait = WebDriverWait(self.driver, 10)
        try:
            # may be redirected to search page directly
            if wait.until(lambda driver: '/login' in driver.current_url or '/search' in driver.current_url):
                # verify user is created in database
                with app.app_context():
                    user = Member.query.filter_by(username=TEST_USER['username']).first()
                    self.assertIsNotNone(user)
                    self.assertEqual(user.email, TEST_USER['email'])
                    
                    # verify user role is created
                    role = UserRole.query.filter_by(username=TEST_USER['username']).first()
                    self.assertIsNotNone(role)
                    self.assertEqual(role.role, 'user')
            else:
                self.fail("Registration failed - not redirected to login or search page")
                
        except TimeoutException:
            self.fail("Registration failed - timeout waiting for redirect")

    def test_successful_login(self):
        """Test user login with valid credentials"""
        # Create a test user first
        with app.app_context():
            from werkzeug.security import generate_password_hash
            test_member = Member(
                username=TEST_USER['username'],
                firstName=TEST_USER['first_name'],
                lastName=TEST_USER['last_name'],
                email=TEST_USER['email'],
                hashPwd=generate_password_hash(TEST_USER['password'])
            )
            db.session.add(test_member)
            db.session.add(UserRole(username=test_member.username, role='user'))
            db.session.commit()
        
        # Go to login page
        self.driver.get(f'http://localhost:{self.port}/login')
        
        # wait for page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        
        # Fill out the login form
        self.driver.find_element(By.ID, 'username').send_keys(TEST_USER['username'])
        self.driver.find_element(By.ID, 'password').send_keys(TEST_USER['password'])
        
        # ensure page is loaded and submit button is visible
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
        )
        
        # use JavaScript to click button instead of direct click
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)  # wait for scroll to complete
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # Check if login was successful and redirected to search page
        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(EC.url_contains('/search'))
            
            # Verify flash message
            flash_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'alert'))).text
            self.assertIn(f'Welcome back, {TEST_USER["username"]}', flash_message)
            
        except TimeoutException:
            self.fail("Login failed - did not redirect to search page")

    def test_failed_login_incorrect_password(self):
        """Test login with incorrect password"""
        # Create a test user first
        with app.app_context():
            from werkzeug.security import generate_password_hash
            test_member = Member(
                username=TEST_USER['username'],
                firstName=TEST_USER['first_name'],
                lastName=TEST_USER['last_name'],
                email=TEST_USER['email'],
                hashPwd=generate_password_hash(TEST_USER['password'])
            )
            db.session.add(test_member)
            db.session.add(UserRole(username=test_member.username, role='user'))
            db.session.commit()
        
        # Go to login page
        self.driver.get(f'http://localhost:{self.port}/login')
        
        # wait for page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        
        # Fill out the login form with incorrect password
        self.driver.find_element(By.ID, 'username').send_keys(TEST_USER['username'])
        self.driver.find_element(By.ID, 'password').send_keys('wrong_password')
        
        # ensure page is loaded and submit button is visible
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
        )
        
        # use JavaScript to click button instead of direct click
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)  # wait for scroll to complete
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # Check if login failed and error message is displayed
        wait = WebDriverWait(self.driver, 10)
        try:
            # Verify flash message for unsuccessful login
            flash_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'alert-danger')))
            self.assertIn('Login Unsuccessful', flash_element.text)
            
            # Verify we're still on the login page
            self.assertIn('/login', self.driver.current_url)
            
        except TimeoutException:
            self.fail("Expected error message did not appear")

    def test_failed_login_nonexistent_user(self):
        """Test login with a username that doesn't exist"""
        # Go to login page
        self.driver.get(f'http://localhost:{self.port}/login')
        
        # wait for page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        
        # Fill out the login form with non-existent username
        self.driver.find_element(By.ID, 'username').send_keys('nonexistent_user')
        self.driver.find_element(By.ID, 'password').send_keys('any_password')
        
        # ensure page is loaded and submit button is visible
        submit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"]'))
        )
        
        # use JavaScript to click button instead of direct click
        self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)  # wait for scroll to complete
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # Check if login failed and error message is displayed
        wait = WebDriverWait(self.driver, 10)
        try:
            # Verify flash message for unsuccessful login
            flash_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'alert-danger')))
            self.assertIn('Login Unsuccessful', flash_element.text)
            
            # Verify we're still on the login page
            self.assertIn('/login', self.driver.current_url)
            
        except TimeoutException:
            self.fail("Expected error message did not appear")

    def test_login_required_redirect(self):
        """Test that protected routes redirect to login page"""
        # Try to access a protected route (search) when not logged in
        self.driver.get(f'http://localhost:{self.port}/search')
        
        # Check if redirected to login page with next parameter
        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(EC.url_contains('/login?next=%2Fsearch'))
            
        except TimeoutException:
            self.fail("Not redirected to login page when accessing protected route")

if __name__ == '__main__':
    unittest.main()
