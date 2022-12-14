import pytest

from location_coordinates import *


@pytest.fixture
def coords():
    return LocationCoordinates(latitude="40.8153762",
                               longitude="-73.0451085")


def test_ncei_boundingbox(coords):
    # https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation
    assert coords.ncei_boundingbox(5, "miles") == "40.888,-73.117,40.743,-72.973"
    assert coords.ncei_boundingbox(5, "km") == "40.860,-73.090,40.770,-73.000"
    with pytest.raises(ValueError):
        coords.ncei_boundingbox(5, "na")


def test_googleapi_latlngbounds_urlvalue(coords):
    # https://developers.google.com/maps/documentation/javascript/reference/coordinates#LatLngBounds.toUrlValue
    assert coords.googleapi_latlngbounds_urlvalue(5, "miles") == "40.743,-73.117,40.888,-72.973"
    assert coords.googleapi_latlngbounds_urlvalue(5, "km") == "40.770,-73.090,40.860,-73.000"
    with pytest.raises(ValueError):
        coords.googleapi_latlngbounds_urlvalue(5, "na")


def test_distance_from():
    origin = LocationCoordinates(latitude="41.318581",
                                 longitude="-96.346288")
    other = LocationCoordinates(latitude="41.55361",
                                longitude="-96.14056")
    assert origin.distance_from(other, 'miles') == pytest.approx(21.576, abs=1e-3)
    with pytest.raises(ValueError):
        origin.distance_from(other, 'na')
