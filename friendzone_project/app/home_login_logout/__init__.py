from flask import Blueprint

# Initialises instance (routes then reference this instance)
home_bp = Blueprint("home", __name__)

from . import routes  # Import routes to associate them with the Blueprint

