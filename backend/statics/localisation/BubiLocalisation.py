import requests
import json
from backend.statics.localisation.toolsLocalisation import haversine_distance


def bubi_location():
    """
    Get all Bubi bike-sharing station locations.
    Returns a dictionary with station names as keys and (lat, lon) tuples as values.
    """
    response = requests.get(
        "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/bicycle-rental.json?key=bkk-web&version=4")
    content = response.content

    data_decode = content.decode('utf-8')  # utf-8 is the most common

    data = json.loads(data_decode)['data']['list']
    Stations = {}

    for station in data:
        Stations[station['name']] = (station['lat'], station['lon'])

    return Stations


def find_nearest_station(coordinates, stations):
    """
    Find the nearest Bubi station to given coordinates.
    
    Args:
        coordinates: Tuple of (latitude, longitude)
        stations: Dictionary of stations with names as keys and (lat, lon) tuples as values
    
    Returns:
        Tuple of (station_name, station_coords, distance_in_km) or None if no stations found
    """
    nearest = None
    min_distance = float('inf')

    for name, coords in stations.items():
        distance = haversine_distance(coordinates, coords)
        if distance < min_distance:
            min_distance = distance
            nearest = (name, coords, distance)

    return nearest
