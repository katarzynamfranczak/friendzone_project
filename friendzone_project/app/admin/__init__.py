from flask import Blueprint

# Initialises instance (routes then reference this instance)
admin_bp = Blueprint("admin", __name__)

from . import routes  # Import routes to associate them with the Blueprint

