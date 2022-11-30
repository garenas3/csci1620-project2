import requests


def get_zipcode_location(username: str, zipcode: str):
    """Get the ZIP code location using GeoNames web services.

    For more information about GeoNames web services:
    https://www.geonames.org/export/web-services.html

    Args:
        username: The username to use for the application.
        zipcode: The US postal code to use for the search.
    Returns:
        The coordinates associated with the zip code.
    """
    payload = {                 # maxRows <= 500 uses 2 credits per request
        "postalcode": zipcode,  # ZIP codes are exclusive to US
        "country": "US",        # restrict results to US
        "radius": 30,           # 30 km is max radius for free accounts
        "maxRows": 1,           # assume first row is correct latitude and longitude
        "username": username    # username should be unique to application
    }
    r = requests.get("https://secure.geonames.org/postalCodeSearchJSON", params=payload)
    try:
        response = r.json()
        if not r.ok:
            if response:
                error_message = response["status"]["message"]
                error_code = response["status"]["value"]
                raise Exception(f"GeoNames Webservice Exception ({error_code}): {error_message}")
            else:
                r.raise_for_status()
        result = response["postalCodes"][0]
        return {"latitude": result["lat"], "longitude": result["lng"]}
    except requests.exceptions.JSONDecodeError:
        raise Exception("Unable to parse JSON")


def load_username() -> str:
    """Load the GeoNames username from the file geonames.txt."""
    with open("geonames.txt", "r") as fh:
        return fh.read().strip()


def main():
    username = load_username()
    zipcode = input("Enter ZIP code: ")
    location = get_zipcode_location(username=username, zipcode=zipcode)
    print(location)


if __name__ == "__main__":
    main()
