import requests
from math import radians, sin, cos, sqrt, atan2


def haversine_distance(coord1, coord2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    R = 6371  # Radius of earth in kilometers

    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def get_coordinates(address):
    """
    Get coordinates (latitude, longitude) from a given address.
    Uses OpenStreetMap Nominatim API directly.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "BudaTrip/1.0"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if data:
            location = data[0]
            return {
                "address": location. get("display_name"),
                "latitude": float(location. get("lat")),
                "longitude": float(location.get("lon"))
            }
        else:
            return "Address not found"

    except Exception as e:
        return f"Error: {e}"