from typing import Literal

import requests
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from location_coordinates import LocationCoordinates


def get_nearby_stations(token: str, location: LocationCoordinates,
                        radius: float, unit: Literal['miles', 'km']):
    """Retrieve a list of nearby stations.

    https://www.ncdc.noaa.gov/cdo-web/webservices/v2

    Args:
        token: The NCDC web service token used to retrieve the data.
        location: The coordinates to use when searching.
        radius: The distance to search from the center of the search location.
        unit: The unit to use for the search radius. Either miles or km.
    Returns:
        A list of stations near the given search coordinates sorted from nearest to farthest.
    """
    payload = {
        'extent': location.googleapi_latlngbounds_urlvalue(radius, unit),
        'datasetid': 'NORMAL_ANN'  # Normals Annual/Seasonal
    }
    r = requests.get('https://www.ncei.noaa.gov/cdo-web/api/v2/stations',
                     params=payload, headers={'token': token})
    try:
        response = r.json()
        stations = response['results']
        return stations
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError('Unable to parse JSON')


def load_token() -> str:
    """Load the NCDC service token from the file ncdc.txt."""
    with open("ncdc.txt", "r") as fh:
        return fh.read().strip()


class GetNearbyStationsAsyncController(QObject):
    """Send the nearby stations request asynchronously.

    Asynchronous requests require the use of a worker object and worker
    thread. The purpose of this AsyncController is to bundle these two
    objects together and only expose some signals from the worker. The
    worker and worker thread do not exist until sendRequest() is called
    and are destroyed thereafter. This is why the AsyncController has
    its own signals to use instead of allowing access to the worker's
    signals.
    """
    result_ready = pyqtSignal(dict)
    error_raised = pyqtSignal(str)

    def __init__(self, token: str) -> None:
        """Initialize the AsyncController.

        The worker and worker thread need to be class instance
        variables otherwise they will be deleted before processing.
        """
        super().__init__()
        self.token = token
        self._worker = None
        self._worker_thread = None

    def sendRequest(self, location: LocationCoordinates, search_radius: float,
                    unit: Literal['miles', 'km']) -> None:
        """Start up a thread to send the request.

        Connection chain adapted from blog and official documentation.

        https://doc.qt.io/qt-5/qthread.html

        https://mayaposch.wordpress.com/2011/11/01/how-to-really-truly-use-qthreads-the-full-explanation/

        A lot of PyQt QThread examples use a subclass then call
        QThread.terminate() and QThread.wait() for cleanup, but this is
        discouraged for a variety of reasons.

        https://www.vikingsoftware.com/blog/how-to-use-qthread-properly/

        https://www.qt.io/blog/2010/06/17/youre-doing-it-wrong
        """
        self._worker_thread = QThread()
        self._worker = _GetNearbyStationsAsyncWorker(self.token, location, search_radius, unit)
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.doWork)
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)

        self._worker.result_ready.connect(self.result_ready)
        self._worker.error_raised.connect(self.error_raised)

        self._worker_thread.start()


class _GetNearbyStationsAsyncWorker(QObject):
    """Worker to perform asynchronous fetch of nearby stations."""
    result_ready = pyqtSignal(dict)
    error_raised = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, token: str, location: LocationCoordinates,
                 radius: float, unit: Literal['miles', 'km']) -> None:
        super().__init__()
        self.token = token
        self.location = location
        self.radius = radius
        self.unit = unit

    def doWork(self) -> None:
        try:
            result = get_nearby_stations(self.token, self.location,
                                         self.radius, self.unit)
            self.result_ready.emit(result)
        except RuntimeError as error:
            self.error_raised.emit(str(error))
        finally:
            self.finished.emit()


def main():
    token = load_token()
    location = LocationCoordinates(latitude="41.318581", longitude="-96.346288")
    stations = get_nearby_stations(token, location, 15, "miles")
    for station in stations:
        print(station)


if __name__ == "__main__":
    main()
