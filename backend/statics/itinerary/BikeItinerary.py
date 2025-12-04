"""
Functions to compute itineraries using Bubi bike-sharing stations.
This module handles route calculation with Bubi stations (walk -> bike -> walk).
"""

import requests
from backend.statics.localisation import Location


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





def get_route_with_bubi(start_coords, end_coords):
    """
    Calculate a route using Bubi bike-sharing stations.

    Args:
        start_coords: Tuple of (latitude, longitude) for start point
        end_coords: Tuple of (latitude, longitude) for end point

    Returns:
        Dictionary with route information including stations and segments, or None if error
    """
    start_lat, start_lon = start_coords
    end_lat, end_lon = end_coords

    # Get all Bubi stations
    stations = Location.bubi_location()

    # Find nearest stations to start and end points
    start_station = Location.find_nearest_station((start_lat, start_lon), stations)
    end_station = Location.find_nearest_station((end_lat, end_lon), stations)

    if not start_station or not end_station:
        return None

    start_station_name, start_station_coords, start_distance = start_station
    end_station_name, end_station_coords, end_distance = end_station

    # Calculate route segments
    walk_to_start = get_route((start_lat, start_lon), start_station_coords, mode='foot')
    bike_route = get_route(start_station_coords, end_station_coords, mode='bike')
    walk_from_end = get_route(end_station_coords, (end_lat, end_lon), mode='foot')

    # Calculate totals
    total_distance = (
            (walk_to_start['distance'] if walk_to_start else 0) +
            (bike_route['distance'] if bike_route else 0) +
            (walk_from_end['distance'] if walk_from_end else 0)
    )

    total_duration = (
            (walk_to_start['duration'] if walk_to_start else 0) +
            (bike_route['duration'] if bike_route else 0) +
            (walk_from_end['duration'] if walk_from_end else 0)
    )

    return {
        'start_station': {
            'name': start_station_name,
            'lat': start_station_coords[0],
            'lon': start_station_coords[1],
            'distance': round(start_distance, 2)
        },
        'end_station': {
            'name': end_station_name,
            'lat': end_station_coords[0],
            'lon': end_station_coords[1],
            'distance': round(end_distance, 2)
        },
        'routes': {
            'walk_to_start': walk_to_start,
            'bike': bike_route,
            'walk_from_end': walk_from_end
        },
        'total_distance': total_distance,
        'total_duration': total_duration
    }
