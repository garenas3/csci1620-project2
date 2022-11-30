import csv
from typing import Any


def load(filename: str = "programdata.csv") -> dict[str, dict[str, Any]]:
    """Load the program cache from a file."""
    try:
        with open(filename, 'r', newline='') as fh:
            result = {}
            reader = csv.DictReader(fh)
            for row in reader:
                zipcode = row['zipcode']
                result[zipcode] = row
            return result
    except FileNotFoundError:
        return {}


def save(data: dict[str, str],
         filename: str = "programdata.csv") -> None:
    """Save the program cache to a file."""
    if not data:
        return
    try:
        with open(filename, 'w', newline='') as fh:
            writer = csv.DictWriter(fh, ["zipcode", "latitude", "longitude", "city"])
            writer.writeheader()
            for zipcode, coords in data.items():
                writer.writerow(coords)
    except KeyError:
        raise RuntimeError("Unexpected program data format")
