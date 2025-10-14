import requests

def get_route(start_coords, end_coords, mode='cycling'):

    try:
        url = f"http://router.project-osrm.org/route/v1/{mode}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
        params = {
            'overview': 'full',
            'geometries': 'geojson',
            'steps': 'true'
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data['code'] == 'Ok':
            route = data['routes'][0]
            return {
                'coordinates': route['geometry']['coordinates'],
                'distance': route['distance'],
                'duration': route['duration'],
                'steps': route['legs'][0]['steps']
            }
        else:
            print(f"Error of routing: {data['code']}")
            return None

    except Exception as e:
        print(f"Error while curling the itinerary: {e}")
        return None
