from flask import Blueprint

# Initialises instance (routes then reference this instance)
messages_bp = Blueprint("messages", __name__)

from . import routes  # Import routes to associate them with the Blueprint

