# utils.py

from math import radians, cos, sin, asin, sqrt

# https://en.wikipedia.org/wiki/Haversine_formula
def calculate_harversine(lat_x, lon_x, lat_y, lon_y):
    EARTH_RADIUS = 6371
    dist_lat_in_radians = radians(lat_y - lat_x)
    dist_lon_in_radians = radians(lon_y - lon_x)
    lat_x_in_radians = radians(lat_x)
    lat_y_in_radians = radians(lat_y)

    haversine_term = (
        sin(dist_lat_in_radians / 2) ** 2
        + cos(lat_x_in_radians)
        * cos(lat_y_in_radians)
        * sin(dist_lon_in_radians / 2) ** 2
    )

    return EARTH_RADIUS * 2 * asin(sqrt(haversine_term))
