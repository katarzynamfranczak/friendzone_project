import string
import requests
from flask import current_app, flash, render_template, session, Request
from datetime import datetime, time, timedelta
from collections import defaultdict


class BaseValidator:
    """Base class for validation operations"""

    @staticmethod
    def validate(value: str, allowed_chars: set) -> bool:
        """Generic validator for checking character sets"""
        return all(char in allowed_chars for char in value) # Check input against set and return True only if all match


# Inherits functionality of BaseValidator
class Validators(BaseValidator):
    """Specific validators for the application"""

    @classmethod
    def contains_only_letters(cls, value: str) -> bool:
        """Validator function to check if a string contains only letters"""
        allowed_chars = set(string.ascii_letters + "'" + "-" + " ")
        return cls.validate(value, allowed_chars)


class DataExtractor:

    @staticmethod
    def get_search_form_data(request: Request) -> tuple:
        """Function to get input from request and validate chars"""

        location = request.form.get('location')  # Get location input
        radius = request.form.get('radius')  # Get radius
        activity = request.form.get('activities')  # Get activity
        timeslot = request.form.get('timeslots')  # Get timeslot
        days = request.form.get('days')  # Get day(s)

        valid_chars = Validators.contains_only_letters(location)
        if not valid_chars:
            location = None

        return location, radius, activity, timeslot, days


class APIManager:
    """Base class for managing API interactions"""

    def __init__(self, api_key_config: str, country_config: str = None) -> None:
        self.api_key = current_app.config[api_key_config]
        self.country = current_app.config.get(country_config)


# Functions to find lat / lon and other location details inheriting from Base class
class LocationManager(APIManager):
    def __init__(self) -> None:
        super().__init__('LOC_API_KEY', 'COUNTRY')

    def get_lat_lon(self, query: str) -> tuple | None:
        """Takes human-readable location input and outputs lat & lon"""
        try:
            result = requests.get(
                f'https://us1.locationiq.com/v1/search?key={self.api_key}&format=json&q={query}+{self.country}',
                timeout=5)

            data = result.json()
            return (float(data[0]['lat']), float(data[0]['lon'])) if data else None # return float tuple

        except requests.Timeout:
            current_app.logger.error(f"Location API timeout for query: {query}")
            return None


class ActivitySearcher(APIManager):
    def __init__(self) -> None:
        super().__init__('HP_API_KEY')

    def search(self, lat: str, lon: str, radius: str, activity: str) -> dict | None:
        """Uses lat, lon & user input to query 3rd party database & return venues"""
        try:
            url = f'https://discover.search.hereapi.com/v1/discover?apiKey={self.api_key}&in=circle:{lat},{lon};r={radius}&q={activity}&limit=15'
            result = requests.get(url, timeout=5)
            return result.json() if result.status_code == 200 else None

        except requests.Timeout:
            current_app.logger.error(f"HerePlaces API timeout for query: {lat, lon, activity}")
            return None


# Functions to format the data effectively
class DataFormatter():
    """A number of functions relating to consistent data formatting"""

    def dictionary_sorter(self, data: dict) -> dict:
        """Filter large output values to only relevant data"""
        nested_dict = defaultdict(dict) # defaultdict allows smoother dynamic dict creation
        start_time = session['start_time_for_filter']
        open_venue = 0

        for count, venue in enumerate(data['items'], 1):

            # Only include venue if opening times match searched criteria
            if self.is_venue_open(venue, session['day_for_filter'], start_time, start_time + 3):
                open_venue += 1
                nested_dict[count] = {
                    ' ': str(open_venue),
                    'Name': venue['title'],
                    'Address': self.address_builder(venue['address']),
                    'Website': self.get_website(venue),
                    'Opening Hours': self.get_opening_times(venue)
                }

        return dict(nested_dict)

    @staticmethod
    def address_builder(address_data: dict) -> str:
        """Consistent address formatting"""

        address = ""

        if 'houseNumber' in address_data:
            address_1 = address_data['houseNumber']
            address += address_1 + ', '

        if 'street' in address_data:
            address_2 = address_data['street']
            address += address_2

        if 'district' in address_data:
            address_3 = address_data['district']
            address += ', ' + address_3

        if 'postalCode' in address_data:
            address_4 = address_data['postalCode']
            address += ', ' + address_4

        return address

    @staticmethod
    def get_website(venue: dict) -> list | str:
        """Return web address if exists"""

        if 'contacts' in venue and venue['contacts']:
            if 'www' in venue['contacts'][0]:
                return venue['contacts'][0]['www'][0]['value']
        else:
            return ""

    @staticmethod
    def get_opening_times(venue: dict) -> str:
        """Return opening times if exists"""

        if 'openingHours' in venue and venue['openingHours']:
            value = venue['openingHours'][0]['text']
            if value:
                return value
        else:
            return ""

    @staticmethod
    def parse_duration(duration_str):
        """Changes time string into timedelta ti use in isVenueOpen"""
        hours = 0
        minutes = 0

        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0])  # Extract hours
            duration_str = duration_str.split('H')[1]  # Pass on just mins to next if

        if 'M' in duration_str:
            minutes = int(duration_str.split('M')[0])  # Extract mins

        return timedelta(hours=hours, minutes=minutes)

    @staticmethod
    def is_venue_open(data, check_day, check_start_hour, check_end_hour):
        """
        Determines if a venue is open during a specified time window on a specified day.

        Args:
        - data: A dictionary containing the venue's opening hours.
        - check_day: The day to check (e.g. "MO" for Monday).
        - check_start_hour: The starting hour to check (e.g. 12 for 12 PM).
        - check_end_hour: The ending hour to check (e.g. 15 for 3 PM).

        Returns:
        - True if the venue is open during the specified time window, False otherwise.
        """

        # Handle missing / empty opening hours
        if "openingHours" not in data:
            return True

        check_start_time = time(check_start_hour)
        check_end_time = time(check_end_hour)

        for entry in data["openingHours"][0]["structured"]:
            # Check day exists in recurrence
            recurrence = entry["recurrence"]
            if f"BYDAY:{check_day}" not in recurrence:
                continue

            start_str = entry["start"][1:]  # Remove the T at start
            start_time = time(
                hour=int(start_str[:2]),
                minute=int(start_str[2:4]),
                second=int(start_str[4:6]))

            duration = DataFormatter.parse_duration(entry["duration"][2:])

            # Calculate closing time
            closing_time = (
                    datetime.combine(datetime.today(), start_time) + duration
            ).time()

            # Check if searched time within these hours
            if check_start_time >= start_time and check_end_time <= closing_time:
                return True

        return False  # If no match



class SearchSessionManager:
    """Manages search session configuration and conversions"""

    @staticmethod
    def save_search_session(location, radius, activity, timeslot, days, lat, lon):
        """Save session data for later functions"""
        try:
            display_activities = {
                'bakery+baked+goods+doughnut+shop': 'Bakery',
                'bar-pub': 'Bar',
                'cinema': 'Cinema',
                'coffee+tea+coffee-tea': 'Coffee Shop'
            }

            radius_conversion = {
                '1600': '1',
                '4820': '3',
                '8000': '5'
            }

            day_conversion = {
                'MON': 'MO', 'TUE': 'TU', 'WED': 'WE',
                'THU': 'TH', 'FRI': 'FR', 'SAT': 'SA',
                'SUN': 'SU',
                'WEEKDAYS': 'MO,TU,WE,TH,FR',
                'WEEKENDS': 'SA,SU'
            }

            time_conversion = {
                '9:00 - 12:00': 9,
                '12:00 - 15:00': 12,
                '15:00 - 18:00': 15,
                '18:00 - 21:00': 18
            }

            # Save session variables
            session.update({
                'location': location,
                'radius': radius,
                'db_radius': radius_conversion[radius],
                'api_activity': activity,
                'display_activity': display_activities[activity],
                'timeslot': timeslot,
                'days': days,
                'lat': round(lat, 8),
                'lon': round(lon, 8),
                'day_for_filter': day_conversion[days],
                'start_time_for_filter': time_conversion[timeslot]
            })

        except Exception as e:
            current_app.logger.error(f"Error: Cannot save to session {e}")


def display_search_page(error):
    """Display search page, with or without error message"""

    # Populate dropdowns
    radius, activities, timeslots, days = get_dropdown_options()

    # Default value for text field (There is a placeholder in the search.html)
    location = ''

    if error:
        # Flash error message
        flash('Location is required. Please enter a valid place name.', 'error')

    return render_template(
        "search.html",
        location=location,
        radius=radius,
        activities=activities,
        timeslots=timeslots,
        days=days
    )


def get_dropdown_options():
    """Dictionaries containing dropdown values"""

    radius = [
        {'value': '1600', 'label': '1 mile'},
        {'value': '4820', 'label': '3 miles', 'selected': True},  # pre-selected
        {'value': '8000', 'label': '5 miles'}
    ]

    activities = [
        {'value': 'bakery+baked+goods+doughnut+shop', 'label': 'Bakery'},
        {'value': 'bar-pub', 'label': 'Bar'},
        {'value': 'cinema', 'label': 'Cinema'},
        {'value': 'coffee+tea+coffee-tea', 'label': 'Coffee Shop','selected': True},
    ]

    timeslots = [
        {'value': '9:00 - 12:00', 'label': 'Morning: 9am - 12pm'},
        {'value': '12:00 - 15:00', 'label': 'Lunchtime: 12pm - 3pm'},
        {'value': '15:00 - 18:00', 'label': 'Afternoon: 3pm - 6pm'},
        {'value': '18:00 - 21:00', 'label': 'Evening: 6pm - 9pm', 'selected': True}
    ]

    days = [
        {'value': 'MON', 'label': 'Monday'},
        {'value': 'TUE', 'label': 'Tuesday'},
        {'value': 'WED', 'label': 'Wednesday'},
        {'value': 'THU', 'label': 'Thursday'},
        {'value': 'FRI', 'label': 'Friday'},
        {'value': 'SAT', 'label': 'Saturday'},
        {'value': 'SUN', 'label': 'Sunday'},
        {'value': 'WEEKDAYS', 'label': 'Any Weekday', 'selected': True},
        {'value': 'WEEKENDS', 'label': 'Weekends'}
    ]

    return radius, activities, timeslots, days


def use_location(location):
    """If location is valid, return latitude / longitude"""

    if not location:
        return None, None

    # Initialise Location Manager
    lat_lon_finder = LocationManager()
    lat, lon = lat_lon_finder.get_lat_lon(location)
    return lat, lon


def find_and_format_activity(lat, lon, radius, activity):
    """Search for & format activity results"""

    # Initialise ActivitySearcher
    activity_searcher = ActivitySearcher()
    search_results = activity_searcher.search(lat, lon, radius, activity)

    # Initialise DataFormatter
    data_formatter = DataFormatter()
    formated_results = data_formatter.dictionary_sorter(search_results)

    return formated_results
