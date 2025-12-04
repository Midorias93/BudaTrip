from backend.statics.localisation.UserLocalisation import get_my_coordinates
import requests


def get_weather():
    latitude, longitude = get_my_coordinates()
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        current = data["current"]

        return {'temperature': current['temperature_2m'], 'precipitation': current['precipitation'],
                       'wind_speed': current['wind_speed_10m']}

    except requests.exceptions.RequestException as e:
        print(f"Error while getting weather : {e}")
        return None