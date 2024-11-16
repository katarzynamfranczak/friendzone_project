from flask import Flask
from friendzone_project.app.extensions import bcrypt
import os
from datetime import timedelta

from .search import search_bp
from .home_login_logout import home_bp
from .admin import admin_bp
from .messages import messages_bp
from .match import match_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # Load config (API keys, DB values)
    app.config['SECRET_KEY'] = os.urandom(24) # Generate cryptographic key for secure session storage
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    bcrypt.init_app(app)  # Initialize bcrypt with the app

    # Register Blueprints
    app.register_blueprint(search_bp, url_prefix="/search")
    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(messages_bp, url_prefix="/messages")
    app.register_blueprint(admin_bp, url_prefix="/promote")
    app.register_blueprint(match_bp, url_prefix="/match")

    return app
