from flask_bcrypt import Bcrypt
from flask import session, g
import mysql.connector

from ..config import Config

# Create Bcrypt class instance to enable password hashing
bcrypt = Bcrypt()


def _clear_session_except(keep_keys):
    """
    Clears all session variables except the ones specified in keep_keys.

    Args: keep_keys: A list of keys to keep in the session.

    Raises: TypeError if not list / tuple
    """
    if not isinstance(keep_keys, (tuple, list)):
        raise TypeError("keep_keys must be a list or tuple")

    keys_to_keep = {key: session[key] for key in keep_keys if key in session}
    session.clear()
    session.update(keys_to_keep)  # Restores the keys we want to keep


def _get_current_user():
    user = None
    if 'user' in session:
        user = session['username']
        db = _get_database()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE user_name = '{user}';")
        user = cursor.fetchone()
        cursor.close()
    return user


def _get_database():
    if not hasattr(g, 'databasename_db'):
        g.databasename_db = _connect_to_database()
    return g.databasename_db


def _connect_to_database():
    """Connects to the FriendZone database."""
    host = Config.HOST
    user = Config.USER
    password = Config.PASSWORD
    database = Config.DATABASE

    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return cnx
    except Exception as e:
        # raise RuntimeError(f"Failed to connect to the database: {e}")
        print(f"Failed to connect to the database: {e}")


