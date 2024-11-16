from flask import request, render_template, session, current_app, flash, redirect, url_for

from . import search_bp
from friendzone_project.app.search.services import DataExtractor, use_location, display_search_page, find_and_format_activity, SearchSessionManager
from friendzone_project.app.extensions import _clear_session_except


# Search Page & Results
@search_bp.route("/", methods=['GET','POST'])
def search():
    if request.method == 'POST':
        try:
            # Get data from request in a usable format
            location, radius, activity, timeslot, days = DataExtractor.get_search_form_data(request)
            # Find the latitude / longitude of the location
            lat, lon = use_location(location)
            # Validate location & display search page with error if None
            if lat is None:
                return display_search_page(True)

            # Save to session for use in match functions
            SearchSessionManager.save_search_session(location, radius, activity, timeslot, days, lat, lon)

            # Remove unnecessary date from results
            formatted_results = find_and_format_activity(lat, lon, radius, activity)

            session['latest_search'] = formatted_results # Stored results to pass to match functions

            # Display results
            return render_template('results_table_template.html', data=formatted_results, activity=session['display_activity'],
                                   location=location)

        except Exception as e:
            current_app.logger.error(f"Search error : {str(e)}")
            flash(f'An unexpected error occurred. Please try again. {str(e)}', 'error')
            return display_search_page(True)

    # If GET method, display page
    # Make sure only authorised users can access this page - redirect to login page
    if 'username' not in session:
        flash('You need to Log In or Sign Up before you can access that feature', category='error')
        return redirect(url_for('home.login'))

    # Clear previously searched values
    _clear_session_except(['username', 'user_id', 'user_type'])

    # Display page with error if required - only user-defined input is Location
    return display_search_page(False)

