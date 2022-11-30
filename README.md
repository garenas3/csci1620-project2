# CSCI 1620 Project 2

The purpose of this project is to assist in gardening activities. The first
part of the project will be to present frost dates to the user based on the ZIP
code they enter.

To get frost dates from NOAA stations, a location must be determined. This
location can be obtained from GeoNames API.

## GeoNames API

Website: [https://www.geonames.org/](https://www.geonames.org/)

The GeoNames API can be used to input a ZIP code and return a latitude and
longitude coordinate pair.

### How to use GeoNames API

1. Create an account for the application using the [login page](https://www.geonames.org/login).
2. Supply the username as a URL parameter for all requests.

Visit the [GeoNames web services documentation](https://www.geonames.org/export/web-services.html) for more information.

For this application, store the GeoNames username in a file named geonames.txt
in the same directory as this README.
