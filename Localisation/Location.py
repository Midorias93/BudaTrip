import requests
from geopy.geocoders import Nominatim
import json
from math import radians, sin, cos, sqrt, atan2
import geocoder


def get_location():
        g = geocoder.ip('me')
        return {
            'latitude': g.latlng[0] if g.latlng else None,
            'longitude': g.latlng[1] if g.latlng else None,
            'ville': g.city,
            'pays': g.country
        }


def get_my_coordinates() : return (get_location()["latitude"],get_location()["longitude"])

def bubi_location():
    response = requests.get(
        "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/bicycle-rental.json?key=bkk-web&version=4").__dict__
    content = response['_content']

    data_decode = content.decode('utf-8')  # utf-8 est le plus courant

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
    geolocator = Nominatim(user_agent="mon_application")

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


def find_nearest_bkk_stop(conn, lat: float, lon: float):
    """
    Returns the nearest BKK stop from the GTFS stops table.
    Expects a GTFS-like schema with columns: stop_id, stop_name, stop_lat, stop_lon.
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT stop_id, stop_name, stop_lat, stop_lon
        FROM bkk 
        WHERE stop_lat IS NOT NULL AND stop_lon IS NOT NULL
    """)
    nearest = None
    best_dist = float("inf")
    for row in cur.fetchall():
        sid, name, s_lat, s_lon = row
        d = haversine_distance((lat, lon), (s_lat, s_lon))
        if d < best_dist:
            best_dist = d
            nearest = {
                "stop_id": sid,
                "stop_name": name,
                "stop_lat": float(s_lat),
                "stop_lon": float(s_lon),
                "distance_km": round(d, 3),
            }
    return nearest
