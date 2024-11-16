import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from friendzone_project.app.home_login_logout.services import (
    LoginValidators, _InvalidPasswordException
)

# Create test app as some functions rely on Flask context
def create_test_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SOME_CONFIG"] = "test_value"
    app.secret_key = "test_key"  # Required for session usage
    return app

class TestPasswordValidator(unittest.TestCase):

    def setUp(self):
        self.app = create_test_app()
        self.client = self.app.test_client()  # Use the Flask test client
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client_context = self.app.test_request_context()  # Create a request context
        self.client_context.push()

    def tearDown(self):
        self.client_context.pop()  # Remove the request context
        self.app_context.pop()  # Remove the application context

    def test_session_variable_access(self):
        """Check access to session variables"""
        # Set session variable
        with self.client.session_transaction() as session:
            session["user_id"] = 6

        # Test access to variable
        with self.app.test_request_context():
            self.assertEqual(session["user_id"], 6)

    def test_valid_password(self):
        """Check valid password"""
        result = LoginValidators.validate_user_password("Password123")
        self.assertTrue(result)

    def test_invalid_password_too_short(self):
        """Check password length requirement"""
        with self.assertRaises(_InvalidPasswordException):
            LoginValidators.validate_user_password("Pass1")

    def test_invalid_password_no_uppercase(self):
        """Check password uppercase requirement"""
        with self.assertRaises(_InvalidPasswordException):
            LoginValidators.validate_user_password("password123")

    def test_invalid_password_no_lowercase(self):
        """Check password lowercase requirement"""
        with self.assertRaises(_InvalidPasswordException):
            LoginValidators.validate_user_password("PASSWORD123")

    def test_invalid_password_no_numbers(self):
        """Check password digit requirement"""
        with self.assertRaises(_InvalidPasswordException):
            LoginValidators.validate_user_password("PasswordOne")

# Check account can be found on the users database
class TestValidAccount(unittest.TestCase):
    @patch('friendzone_project.app.home_login_logout.services._get_database')  # Replace _get_database with a mock
    def test_valid_account_found(self, mock_get_database):
        """Check email exists in database"""
        # Mock the database connection and cursor
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_get_database.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        # Mock the query result
        mock_cursor.fetchone.return_value = {'user_id': 6}

        result = LoginValidators.valid_account("test@test.com")

        mock_get_database.assert_called_once()
        mock_db.cursor.assert_called_once_with(dictionary=True)
        mock_cursor.execute.assert_called_once_with(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            LIMIT 1;
            """, ["test@test.com"]
        )
        mock_cursor.fetchone.assert_called_once()
        mock_cursor.close.assert_called_once()
        self.assertTrue(result)

    @patch('friendzone_project.app.home_login_logout.services._get_database')  # Replace _get_database with a mock
    def test_valid_account_not_found(self, mock_get_database):
        """Check email does not exist in database"""
        mock_db = MagicMock()
        mock_cursor = MagicMock()
        mock_get_database.return_value = mock_db
        mock_db.cursor.return_value = mock_cursor

        # Query result to return None
        mock_cursor.fetchone.return_value = None

        result = LoginValidators.valid_account("notvalid@test.com")

        mock_cursor.execute.assert_called_once_with(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            LIMIT 1;
            """, ["notvalid@test.com"]
        )

        mock_cursor.fetchone.assert_called_once()
        self.assertFalse(result)

# Check signup email is a valid format
class TestEmailValidator(unittest.TestCase):

    def test_valid_email(self):
        """Check email is valid format"""
        result = LoginValidators.valid_email("test@test.com")
        self.assertTrue(result)

    def test_invalid_email(self):
        """Check email is not a valid format"""
        result = LoginValidators.valid_email("test@t")
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()