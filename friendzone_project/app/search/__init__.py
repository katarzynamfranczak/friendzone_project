from flask import Blueprint

# Initialises instance (routes then reference this instance)
search_bp = Blueprint("search", __name__)

from . import routes  # Import routes to associate them with the Blueprint

