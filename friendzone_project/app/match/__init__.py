from flask import Blueprint

# Initialises instance (routes then reference this instance)
match_bp = Blueprint("match", __name__)

from . import routes  # Import routes to associate them with the Blueprint

