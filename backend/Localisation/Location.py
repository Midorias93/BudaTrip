import requests
from geopy.geocoders import Nominatim
import json
from math import radians, sin, cos, sqrt, atan2
import geocoder
from DataBase import Tables


def get_location():
        g = geocoder.ip('me')
        return {
            'latitude': g.latlng[0] if g.latlng else None,
            'longitude': g.latlng[1] if g.latlng else None,
            'city': g.city,
            'country': g.country
        }


def get_my_coordinates() : return (get_location()["latitude"],get_location()["longitude"])

def bubi_location():
    response = requests.get(
        "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/bicycle-rental.json?key=bkk-web&version=4").__dict__
    content = response['_content']

    data_decode = content.decode('utf-8')  # utf-8 is the most common

    data = json.loads(data_decode)['data']['list']
    Stations = {}

    for station in data :
        Stations[station['name']] = (station['lat'], station['lon'])

    return Stations

def haversine_distance(coord1, coord2):
    R = 6371

    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

def find_nearest_station(coordinates, stations):
    nearest = None
    min_distance = float('inf')

    for name, coords in stations.items():
        distance = haversine_distance(coordinates, coords)
        if distance < min_distance:
            min_distance = distance
            nearest = (name, coords, distance)

    return nearest


def get_coordinates(address):
    geolocator = Nominatim(user_agent="my_application")

    try:
        location = geolocator.geocode(address)

        if location:
            return {
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        else:
            return "Address not found"

    except Exception as e:
        return f"Error: {e}"


async def find_nearest_bkk_stop(lat, lon):
    """
    Returns the nearest BKK stop from the GTFS stops table.
    Expects a GTFS-like schema with columns: stop_id, stop_name, stop_lat, stop_lon.
    """
    conn = await Tables.init_pool()
    rows = await conn.fetch("""
        SELECT stop_id, stop_name, stop_lat, stop_lon
        FROM bkk 
        WHERE stop_lat IS NOT NULL AND stop_lon IS NOT NULL
    """)

    stops = [dict(rows) for rows in rows]

    nearest_stop = None
    min_distance = float('inf')
    user_coords = (lat, lon)
    for stop in stops:
        stop_coords = (stop['stop_lat'], stop['stop_lon'])
        distance = haversine_distance(user_coords, stop_coords)
        if distance < min_distance:
            min_distance = distance
            nearest_stop = stop

    await Tables.close_pool(conn)
    return nearest_stop
