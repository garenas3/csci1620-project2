from typing import Any

import requests
from PyQt5.QtCore import QThread, QObject, pyqtSignal


def get_zipcode_location(username: str, zipcode: str) -> dict[str, Any]:
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
                raise RuntimeError(f"GeoNames Webservice Exception ({error_code}): {error_message}")
            else:
                r.raise_for_status()
        result = response["postalCodes"][0]
        return {"zipcode": zipcode,
                "latitude": result["lat"],
                "longitude": result["lng"],
                "city": f'{result["placeName"]}, {result["ISO3166-2"]}'}
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("Unable to parse JSON")


def load_username() -> str:
    """Load the GeoNames username from the file geonames.txt."""
    with open("geonames.txt", "r") as fh:
        return fh.read().strip()


class GetZIPCodeAsyncController(QObject):
    """Send the ZIP code request asynchronously.

    Asynchronous requests require the use of a worker object and worker
    thread. The purpose of this AsyncController is to bundle these two
    objects together and only expose some signals from the worker. The
    worker and worker thread do not exist until sendRequest() is called
    and are destroyed thereafter. This is why the AsyncController has
    its own signals to use instead of allowing access to the worker's
    signals.
    """
    result_ready = pyqtSignal(dict)

    def __init__(self, username: str) -> None:
        super().__init__()
        self.username = username
        self._worker = None
        self._worker_thread = None

    def sendRequest(self, zipcode: str) -> None:
        """Start up a thread to send the request."""
        self._worker_thread = QThread()
        self._worker = _GetZIPCodeAsyncWorker(self.username, zipcode)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.doWork)
        self._worker.result_ready.connect(self.result_ready)
        self._worker.result_ready.connect(self._worker_thread.quit)
        self._worker.result_ready.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.start()


class _GetZIPCodeAsyncWorker(QObject):
    """Worker to perform asynchronous ZIP code info retrieval."""
    result_ready = pyqtSignal(dict)

    def __init__(self, geonames_username: str, zipcode: str) -> None:
        super().__init__()
        self.geonames_username = geonames_username
        self.zipcode = zipcode

    def doWork(self) -> None:
        result = get_zipcode_location(
            username=self.geonames_username,
            zipcode=self.zipcode
        )
        self.result_ready.emit(result)


def main():
    username = load_username()
    zipcode = input("Enter ZIP code: ")
    location = get_zipcode_location(username=username, zipcode=zipcode)
    print(location)


if __name__ == "__main__":
    main()
