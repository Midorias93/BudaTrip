import requests
from geopy.geocoders import Nominatim
from enum import Enum
import json

class INFO(Enum):
    NONE = 0
    IP = 1
    VILLE = 2
    REGION = 3
    PAYS = 4
    COO = 5

def get_location(info: INFO = INFO.NONE):
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        dic = {"IP": data.get("ip"), "Ville": data.get("city"), "Région": data.get("region"),
               "Pays": data.get("country"), "latitude": float(data.get("loc").split(",")[0]),
               "longitude": float(data.get("loc").split(",")[1])}

        if info == INFO.NONE:
            return dic
        elif info == INFO.IP:
            return dic["IP"]
        elif info == INFO.VILLE:
            return dic["Ville"]
        elif info == INFO.REGION:
            return dic["Région"]
        elif info == INFO.PAYS:
            return dic["Pays"]
        elif info == INFO.COO:
            return dic["latitude"], dic["longitude"]

    except Exception as e:
        print("Erreur :", e)

def get_my_coordinates() : return get_location(INFO.COO)

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


def find_nearest_station(coordinates, stations):
    """
    Trouve la station Bubi la plus proche d'un point donné

    Args:
        coordinates: tuple (latitude, longitude)
        stations: dict des stations Bubi

    Returns:
        tuple (nom_station, coordonnées_station, distance)
    """
    from math import radians, sin, cos, sqrt, atan2

    def haversine_distance(coord1, coord2):
        """Calcule la distance entre deux points en km"""
        R = 6371  # Rayon de la Terre en km

        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    nearest = None
    min_distance = float('inf')

    for name, coords in stations.items():
        distance = haversine_distance(coordinates, coords)
        if distance < min_distance:
            min_distance = distance
            nearest = (name, coords, distance)

    return nearest




def get_coordinates(address):
    """
    Récupère les coordonnées GPS d'une adresse
    """
    # Créer un géocodeur (user_agent est obligatoire)
    geolocator = Nominatim(user_agent="mon_application")

    try:
        # Géocoder l'adresse
        location = geolocator.geocode(address)

        if location:
            return {
                "adresse": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        else:
            return "Adresse non trouvée"

    except Exception as e:
        return f"Erreur: {e}"



