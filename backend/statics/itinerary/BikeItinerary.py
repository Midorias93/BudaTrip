import requests


def get_route(start_coords, end_coords, mode='cycling'):
    """
    Calculate a bike or walking route between two coordinates using OSRM.
    
    Args:
        start_coords: Tuple of (latitude, longitude) for start point
        end_coords: Tuple of (latitude, longitude) for end point
        mode: Transportation mode - 'cycling', 'bike', 'foot', or 'walking' (default: 'cycling')
    
    Returns:
        Dictionary with route information (coordinates, distance, duration, steps) or None if error
    """
    # Normalize mode to OSRM-compatible values
    mode_mapping = {
        'bike': 'cycling',
        'cycling': 'cycling',
        'walking': 'foot',
        'foot': 'foot'
    }
    osrm_mode = mode_mapping.get(mode, mode)
    
    try:
        # OSRM expects lon,lat format, so we swap the coordinates
        url = f"http://router.project-osrm.org/route/v1/{osrm_mode}/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
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
