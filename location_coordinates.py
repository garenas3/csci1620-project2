import math
from typing import Literal


AVG_MILES_PER_PARALLEL = 69.0
AVG_MILES_PER_MERIDIAN = 69.18
AVG_KM_PER_PARALLEL = 111.0
AVG_KM_PER_MERIDIAN = 111.32


class LocationCoordinates:
    """Describes a location using its latitude and longitude."""
    def __init__(self, *, latitude, longitude):
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def __str__(self):
        direction = latitude_compass_direction(self.latitude)
        latitude_string = f'{math.fabs(self.latitude):.3f}°' + f' {direction}' if direction else ''
        direction = longitude_compass_direction(self.longitude)
        longitude_string = f'{math.fabs(self.longitude):.3f}°' + f' {direction}' if direction else ''
        return f'{latitude_string}, {longitude_string}'

    def __repr__(self):
        return f'LocationCoordinates(latitude={self.latitude}, longitude={self.longitude})'

    def ncei_boundingbox(self, radius, unit: Literal['miles', 'km']):
        """Create a bounding box string using this location as the center.

        The bounding box is used to get data surrounding a geographic region.

        https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation

        Args:
            radius: The radius is the distance between the center and the middle of any edge.
            unit: The unit to use when calculating the distance. Either miles or km.
        Returns:
            A string that represents a bounding box around a geographic region.
        """
        latitude_length = to_parallels(radius, unit)
        north = self.latitude + latitude_length
        south = self.latitude - latitude_length
        longitude_length = to_meridians(radius, unit)
        east = self.longitude + longitude_length
        west = self.longitude - longitude_length
        return f'{north:.3f},{west:.3f},{south:.3f},{east:.3f}'

    def googleapi_latlngbounds_urlvalue(self, radius, unit: Literal['miles', 'km']):
        """Create a LatLngBounds URL string around the center of this location.

        A LatLngBounds object is used by the Google Maps API to target a region.

        https://developers.google.com/maps/documentation/javascript/reference/coordinates#LatLngBounds

        Args:
            radius: The radius is the distance between the center and the middle of any edge.
            unit: The unit to use when calculating the distance. Either miles or km.
        Returns:
            A URL value that represents a boundary around a geographic region.
        """
        latitude_length = to_parallels(radius, unit)
        lat_hi = self.latitude + latitude_length
        lat_lo = self.latitude - latitude_length
        longitude_length = to_meridians(radius, unit)
        lng_hi = self.longitude + longitude_length
        lng_lo = self.longitude - longitude_length
        return f'{lat_lo:.3f},{lng_lo:.3f},{lat_hi:.3f},{lng_hi:.3f}'

    def distance_from(self, other, unit: Literal['miles', 'km']):
        """Get the distance from another set of coordinates.

        Args:
            other: Another set of coordinates.
            unit: The unit to use when calculating the distance. Either miles or km.
        Returns:
            A URL value that represents a boundary around a geographic region.
        """
        east_west_distance = from_meridians(other.longitude - self.longitude, unit)
        north_south_distance = from_parallels(other.latitude - self.latitude, unit)
        return math.sqrt((east_west_distance ** 2) + (north_south_distance ** 2))


def latitude_compass_direction(latitude):
    """Determine the compass direction for the given latitude value."""
    value = int(latitude)
    if 0 < value < 90:
        return 'North'
    if 0 > value > -90:
        return 'South'
    return ''


def longitude_compass_direction(longitude):
    """Determine the compass direction for the given longitude value."""
    value = int(longitude)
    if 0 < value < 180:
        return 'East'
    if 0 > value > -180:
        return 'West'
    return ''


def to_parallels(distance: float, unit: Literal['miles', 'km']):
    """Convert distance to approximate parallels.

    Args:
        distance: A distance to convert.
        unit: The unit to use when calculating the distance. Either miles or km.
    Returns:
        The average number of parallels that span the given distance.
    """
    if unit == 'miles':
        return distance / AVG_MILES_PER_PARALLEL
    elif unit == 'km':
        return distance / AVG_KM_PER_PARALLEL
    else:
        raise ValueError('unit must be either miles or km')


def from_parallels(parallels: float, unit: Literal['miles', 'km']):
    """Convert parallels to approximate distance.

    Args:
        parallels: The number of parallels to convert.
        unit: The unit to use when calculating the distance. Either miles or km.
    Returns:
        The average distance that spans the number of parallels.
    """
    if unit == 'miles':
        return parallels * AVG_MILES_PER_PARALLEL
    elif unit == 'km':
        return parallels * AVG_KM_PER_PARALLEL
    else:
        raise ValueError('unit must be either miles or km')


def to_meridians(distance: float, unit: Literal['miles', 'km']):
    """Convert distance to approximate meridians.

    Args:
        distance: A distance to convert.
        unit: The unit to use when calculating the distance. Either miles or km.
    Returns:
        The average number of meridians that span the given distance.
    """
    if unit == 'miles':
        return distance / AVG_MILES_PER_MERIDIAN
    elif unit == 'km':
        return distance / AVG_KM_PER_MERIDIAN
    else:
        raise ValueError('unit must be either miles or km')


def from_meridians(meridians: float, unit: Literal['miles', 'km']):
    """Convert meridians to the approximate distance.

    Args:
        meridians: The number of meridians to convert.
        unit: The unit to use when calculating the distance. Either miles or km.
    Returns:
        The average distance that spans the given number of meridians.
    """
    if unit == 'miles':
        return meridians * AVG_MILES_PER_MERIDIAN
    elif unit == 'km':
        return meridians * AVG_KM_PER_MERIDIAN
    else:
        raise ValueError('unit must be either miles or km')
