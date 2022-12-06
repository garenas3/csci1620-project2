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


def test_distance_from(coords):
    other = LocationCoordinates(latitude="42.8142432",
                                longitude="-73.9395687")
    assert coords.distance_from(other, 'miles') == pytest.approx(8534.43, abs=1e-3)
    assert coords.distance_from(other, 'km') == pytest.approx(22092.3, abs=1e-2)
    with pytest.raises(ValueError):
        coords.distance_from(other, 'na')
