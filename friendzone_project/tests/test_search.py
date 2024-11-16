import unittest
from unittest.mock import patch, MagicMock
import requests
from flask import Flask
from friendzone_project.app.search.services import (
    BaseValidator, Validators, DataExtractor,
    LocationManager, ActivitySearcher,
    display_search_page, get_dropdown_options, use_location,
)


# Create a Flask app instance for tests, including mock config data
def create_test_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SOME_CONFIG"] = "test_value"
    app.config["HP_API_KEY"] = "mock_api_key"  # Add mock API key here
    app.config["LOC_API_KEY"] = "mock_api_key"  # Add mock API key here
    app.secret_key = "test_key"
    return app


# Test validators - all static so straightforward to test
class TestBaseValidator(unittest.TestCase):
    def test_validate_with_permitted_characters(self):
        result = BaseValidator.validate("HelloWorld", set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"))
        self.assertTrue(result)

    def test_validate_with_non_permitted_characters(self):
        result = BaseValidator.validate("Hello123", set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"))
        self.assertFalse(result)


class TestValidators(unittest.TestCase):
    def test_contains_only_letters_valid(self):
        result = Validators.contains_only_letters("Hello World")
        self.assertTrue(result)

    def test_contains_only_letters_invalid(self):
        result = Validators.contains_only_letters("Hello123")
        self.assertFalse(result)


# Check user input
class TestDataExtractor(unittest.TestCase):
    @patch("friendzone_project.app.search.services.requests.get")
    def test_get_search_form_data_valid(self, mock_request):
        mock_request.form = {
            "location": "Croydon",
            "radius": "5",
            "activities": "Bar",
            "timeslots": "12:00 - 15:00",
            "days": "MON"
        }

        with patch.object(Validators, "contains_only_letters", return_value=True): # mock validator function
            result = DataExtractor.get_search_form_data(mock_request)
            self.assertEqual(result, ("Croydon", "5", "Bar", "12:00 - 15:00", "MON"))

    @patch("friendzone_project.app.search.services.requests.get")
    def test_get_search_form_data_invalid_location(self, mock_request):
        mock_request.form = {
            "location": "Croydon123",
            "radius": "5",
            "activities": "Bar",
            "timeslots": "12:00 - 15:00",
            "days": "MON"
        }

        with patch.object(Validators, "contains_only_letters", return_value=False): # mock validator function
            result = DataExtractor.get_search_form_data(mock_request)
            self.assertEqual(result, (None, "5", "Bar", "12:00 - 15:00", "MON"))


# The following functions all require an active context (session or current_app used in the real functions)
# Using helper functions to set up & tear down the context for successful tests.
class TestLocationManager(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("friendzone_project.app.search.services.requests.get")
    def test_get_lat_lon_valid(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"lat": "51.37130490", "lon": "-0.10195700"}] # Mocked response
        mock_get.return_value = mock_response

        location_manager = LocationManager()
        result = location_manager.get_lat_lon("Croydon")
        self.assertEqual(result, (51.37130490, -0.10195700)) # Expected response


class TestActivitySearcher(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("friendzone_project.app.search.services.requests.get")
    def test_search_valid(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200 # Added in a response code value as the actual function requires a 200 code to return valid code.
        mock_response.json.return_value = {'items': [{'title': 'Goose on the Market',
                                                      'contacts': [{'www': [{'value': 'http://www.stonegatepubs.co.uk'}]}]}]}
        mock_get.return_value = mock_response

        searcher = ActivitySearcher()
        result = searcher.search("51.37130490", "-0.10195700", "5000", "Bar")
        self.assertEqual(result, {'items': [{'title': 'Goose on the Market',
                                                      'contacts': [{'www': [{'value': 'http://www.stonegatepubs.co.uk'}]}]}]})

    # If API call times out, make sure the error is logged exactly once.
    @patch("friendzone_project.app.search.services.requests.get", side_effect=requests.Timeout)
    @patch("friendzone_project.app.search.services.current_app.logger")
    def test_search_timeout(self, mock_logger, mock_get):
        searcher = ActivitySearcher()
        result = searcher.search("51.37130490", "-0.10195700", "5000", "Bar")
        self.assertIsNone(result)
        mock_logger.error.assert_called_once()


class TestUtilityFunctions(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # Make sure flash error messages are displaying properly
    @patch("friendzone_project.app.search.services.render_template")
    @patch("friendzone_project.app.search.services.flash")
    def test_display_search_page_with_error(self, mock_flash, mock_render_template):
        display_search_page(True)
        mock_flash.assert_called_once_with(
            "Location is required. Please enter a valid place name.", "error"
        )
        mock_render_template.assert_called_once()

    # Make sure that dropdown options are populated
    def test_get_dropdown_options(self):
        radius, activities, timeslots, days = get_dropdown_options()
        self.assertTrue(len(radius) > 0)
        self.assertTrue(len(activities) > 0)
        self.assertTrue(len(timeslots) > 0)
        self.assertTrue(len(days) > 0)

    # Make sure lat lon are valid
    @patch.object(LocationManager, "get_lat_lon", return_value=(51.37130490, -0.10195700))
    def test_use_location(self, mock_get_lat_lon):
        lat, lon = use_location("Croydon")
        self.assertEqual((lat, lon), (51.37130490, -0.10195700))


if __name__ == "__main__":
    unittest.main()