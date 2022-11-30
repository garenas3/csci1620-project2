import requests

from view import MainWindow


class MainController:
    def __init__(self) -> None:
        self.main_window = MainWindow()
        self.set_up_signals_and_slots()

    def show(self) -> None:
        """Show the main window to the user."""
        self.main_window.show()

    def set_up_signals_and_slots(self) -> None:
        """Set up the signals and slots for the program."""
        self.main_window.close_button.clicked.connect(self.main_window.close)
        self.main_window.submit_button.clicked.connect(self.submit_zip_code)
        self.main_window.zip_code_edit.returnPressed.connect(
            self.submit_zip_code
        )

    def submit_zip_code(self) -> None:
        """Submit the zip code displayed in the zip code line edit."""
        zip_code = self.main_window.zip_code_edit.text()
        self.main_window.zip_code_list.addItems([zip_code])


def get_zipcode_location(username: str, zipcode: str):
    """Get the zip code location using GeoNames web services.

    For more information about GeoNames web services:
    https://www.geonames.org/export/web-services.html

    Args:
        username: The username to use for the application.
        zipcode: The US postal code to use for the search.
    Returns:
        The coordinates associated with the zip code.
    """
    payload = {                 # maxRows <= 500 uses 2 credits per request
        'postalcode': zipcode,  # zip codes are exclusive to US
        'country': 'US',        # restrict results to US
        'radius': 30,           # 30 km is max radius for free accounts
        'maxRows': 1,           # assume first row is correct latitude and longitude
        'username': username    # username should be unique to application
    }
    r = requests.get('https://secure.geonames.org/findNearbyPostalCodesJSON', params=payload)
    try:
        response = r.json()
        if not r.ok:
            if response:
                error_message = response['status']['message']
                error_code = response['status']['value']
                raise Exception(f'GeoNames Webservice Exception ({error_code}): {error_message}')
            else:
                r.raise_for_status()
        result = response['postalCodes'][0]
        return {'latitude': result['lat'], 'longitude': result['lng']}
    except requests.exceptions.JSONDecodeError:
        raise Exception('Unable to parse JSON')


def load_geonames_username() -> str:
    """Load the GeoNames username from the file geonames.txt."""
    with open('geonames.txt', 'r') as fh:
        return fh.read().strip()
