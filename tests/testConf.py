"""
test configuration module

This module is used to store test-related configuration constants and settings.
Currently, all configurations are directly set in the test files.
"""

# database configuration
TEST_DB_URI = 'sqlite:///:memory:'

# test user information
TEST_USER = {
    'username': 'testuser',
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'test@example.com',
    'password': 'password123'
} 