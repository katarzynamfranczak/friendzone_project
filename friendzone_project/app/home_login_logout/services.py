from flask import session
import re

from friendzone_project.app.extensions import _get_database


class _InvalidPasswordException(Exception):
    """Custom exception for invalid passwords."""

    def __init__(self, message):
        super().__init__(message)

class _InvalidEmailException(Exception):
    """Custom exception for invalid passwords."""

    def __init__(self, message):
        super().__init__(message)

class _InvalidAccountException(Exception):
    """Custom exception for invalid passwords."""

    def __init__(self, message):
        super().__init__(message)


class LoginValidators:

    @staticmethod
    def validate_user_password(password: str):
        """
        Validates a user's password based on given criteria.
        Raises an InvalidPasswordException if the criteria are not met.
        Uses session vars to amend css of webpage
        """
        errors = 0
        if len(password) < 9:
            session['length_valid'] = False
            errors += 1
        if not any(char.isupper() for char in password):
            session['upper_valid'] = False
            errors += 1
        if not any(char.islower() for char in password):
            session['lower_valid'] = False
            errors += 1
        if not any(char.isdigit() for char in password):
            session['nums_valid'] = False
            errors += 1
        if errors > 0:
            raise _InvalidPasswordException("Password does not meet requirements.")
        else:
            return True

    @staticmethod
    def reset_password_validation_flags(session):
        """ Set all password validation flags to True before checking."""
        session['length_valid'] = True
        session['upper_valid'] = True
        session['lower_valid'] = True
        session['nums_valid'] = True

    @staticmethod
    def valid_email(email: str) -> bool:
        """Validate an email address."""
        regex = r'^[a-z0-9]+(?:[._]?[a-z0-9])*@(?:\w+\.)+[a-z]{2,}$'
        return bool(re.match(regex, email))

    @staticmethod
    def valid_account(email: str) -> bool:
        db = _get_database()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE email = %s
            LIMIT 1;
            """, [email])
        user_valid = cursor.fetchone()
        cursor.close()

        if not user_valid:
            return False

        return True