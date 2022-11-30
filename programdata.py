import csv


def load(filename: str = "programdata.csv") -> dict[str, str]:
    """Load the program cache from a file."""
    try:
        with open(filename, 'r', newline='') as fh:
            result = {}
            fh.readline()  # read header
            reader = csv.reader(fh)
            for row in reader:
                zipcode = row[0]
                latitude = row[1]
                longitude = row[2]
                result[zipcode] = {"latitude": latitude,
                                   "longitude": longitude}
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
            writer = csv.writer(fh)
            writer.writerow(["zipcode", "latitude", "longitude"])
            for zipcode, coords in data.items():
                writer.writerow(
                    [zipcode, coords["latitude"], coords["longitude"]]
                )
    except KeyError:
        raise RuntimeError("Unexpected program data format")
