import requests
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

def budy_location():
    response = requests.get(
        "https://futar.bkk.hu/api/query/v1/ws/otp/api/where/bicycle-rental.json?key=bkk-web&version=4").__dict__
    content = response['_content']

    data_str = content.decode('utf-8')  # utf-8 est le plus courant

    return json.loads(data_str)
