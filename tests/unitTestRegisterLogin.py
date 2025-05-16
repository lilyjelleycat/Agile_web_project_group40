import unittest
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from app.models import Member, UserRole, Role
from tests.testConf import TEST_DB_URI, TEST_USER

class TestRegisterLogin(unittest.TestCase):
    """Unit tests for registration and login functionality"""
    
    def setUp(self):
        """Setup before tests"""
        print("\n=== Test setup started ===")
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = TEST_DB_URI  # Use in-memory database
        self.app = app.test_client()
        
        # Create database tables
        with app.app_context():
            db.create_all()
            
            # Add roles if needed
            if not Role.query.filter_by(role='user').first():
                db.session.add(Role(role='user'))
                db.session.commit()
        print("=== Test setup completed ===")
    
    def tearDown(self):
        """Cleanup after tests"""
        print("=== Test cleanup started ===")
        with app.app_context():
            db.session.remove()
            db.drop_all()
        print("=== Test cleanup completed ===")
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n>>> STARTING TEST: User Registration")
        # Send POST request to registration route
        response = self.app.post('/register', data={
            'username': TEST_USER['username'],
            'first_name': TEST_USER['first_name'],
            'last_name': TEST_USER['last_name'],
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'confirm_password': TEST_USER['password'],
            'submit': 'Create Account'
        }, follow_redirects=True)
        
        # Validate response and user creation
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            # Check if user exists
            user = Member.query.filter_by(username=TEST_USER['username']).first()
            self.assertIsNotNone(user)
            self.assertEqual(user.firstName, TEST_USER['first_name'])
            self.assertEqual(user.lastName, TEST_USER['last_name'])
            self.assertEqual(user.email, TEST_USER['email'])
            
            # Check role
            role = UserRole.query.filter_by(username=TEST_USER['username']).first()
            self.assertIsNotNone(role)
            self.assertEqual(role.role, 'user')
        print("<<< COMPLETED TEST: User Registration")
    
    def test_user_login_success(self):
        """Test successful user login"""
        print("\n>>> STARTING TEST: Successful User Login")
        # First create a user
        with app.app_context():
            user = Member(
                username='loginuser',
                firstName='Login',
                lastName='User',
                email='login@example.com',
                hashPwd=generate_password_hash('password123')
            )
            db.session.add(user)
            db.session.add(UserRole(username='loginuser', role='user'))
            db.session.commit()
        
        # Attempt to login
        response = self.app.post('/login', data={
            'username': 'loginuser',
            'password': 'password123',
            'remember': False,
            'submit': 'Login'
        }, follow_redirects=True)
        
        # Successful login should redirect to search page
        self.assertEqual(response.status_code, 200)
        # Should see search page or at least not see failure message
        self.assertTrue(b'Search' in response.data or b'Unsuccessful' not in response.data)
        print("<<< COMPLETED TEST: Successful User Login")
    
    def test_user_login_failure(self):
        """Test user login failure (wrong password)"""
        print("\n>>> STARTING TEST: User Login Failure")
        # First create a user
        with app.app_context():
            user = Member(
                username='failuser',
                firstName='Fail',
                lastName='User',
                email='fail@example.com',
                hashPwd=generate_password_hash('correctpass')
            )
            db.session.add(user)
            db.session.add(UserRole(username='failuser', role='user'))
            db.session.commit()
        
        # Attempt to login with wrong password
        response = self.app.post('/login', data={
            'username': 'failuser',
            'password': 'wrongpassword',
            'remember': False,
            'submit': 'Login'
        }, follow_redirects=True)
        
        # Failed login should show error message
        self.assertEqual(response.status_code, 200)
        # Should see login page or error message
        self.assertTrue(b'Login' in response.data or b'Unsuccessful' in response.data)
        print("<<< COMPLETED TEST: User Login Failure")

if __name__ == '__main__':
    unittest.main()
