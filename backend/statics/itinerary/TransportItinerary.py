"""
Functions to compute itineraries using public transport (BKK).

This module handles route calculation using BKK (Budapest Public Transport) Futár API,
which is based on OpenTripPlanner. It provides journey planning functionality for
public transportation in Budapest, including metro, tram, bus, and trolleybus routes.

The BKK API key and base URL are configured in backend/config.py.

Example usage:
    from backend.statics.itinerary.TransportItinerary import get_route
    
    # Calculate route from Parliament to Keleti Station
    route = get_route((47.5071, 19.0459), (47.5000, 19.0844))
    if route:
        print(f"Duration: {route['duration']} seconds")
        for leg in route['legs']:
            print(f"{leg['mode']}: {leg['from']['name']} -> {leg['to']['name']}")

API Endpoints:
    - POST /api/route/transport - Basic public transport routing
    - POST /api/route/transport-with-stops - Routing with nearest stop information
"""

import requests
from backend.statics.localisation import Location
from backend.config import BKK_API_KEY, BKK_API_BASE_URL


def get_route(start_coords, end_coords):
    """
    Calculate a public transport route between two coordinates using BKK API.
    
    Args:
        start_coords: Tuple of (latitude, longitude) for start point
        end_coords: Tuple of (latitude, longitude) for end point
    
    Returns:
        Dictionary with route information including:
        - itineraries: List of possible routes
        - distance: Total distance in meters
        - duration: Total duration in seconds
        - legs: Detailed leg information for each segment
        Or None if error
    """
    try:
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        
        # BKK Futár API endpoint for journey planning (OpenTripPlanner-based)
        url = f"{BKK_API_BASE_URL}/otp/routers/default/plan"
        
        params = {
            'fromPlace': f"{start_lat},{start_lon}",
            'toPlace': f"{end_lat},{end_lon}",
            'mode': 'TRANSIT,WALK',  # Use public transit and walking
            'numItineraries': 3,  # Get up to 3 alternative routes
            'maxWalkDistance': 1000,  # Maximum walking distance in meters
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'plan' in data and 'itineraries' in data['plan']:
                itineraries = data['plan']['itineraries']
                
                if not itineraries:
                    print("No itineraries found")
                    return None
                
                # Process and return the best (first) itinerary
                best_itinerary = itineraries[0]
                
                # Extract route details
                route_info = {
                    'duration': best_itinerary.get('duration', 0),
                    'distance': sum(leg.get('distance', 0) for leg in best_itinerary.get('legs', [])),
                    'start_time': best_itinerary.get('startTime'),
                    'end_time': best_itinerary.get('endTime'),
                    'legs': []
                }
                
                # Process each leg of the journey
                for leg in best_itinerary.get('legs', []):
                    leg_info = {
                        'mode': leg.get('mode'),
                        'from': {
                            'name': leg.get('from', {}).get('name'),
                            'lat': leg.get('from', {}).get('lat'),
                            'lon': leg.get('from', {}).get('lon')
                        },
                        'to': {
                            'name': leg.get('to', {}).get('name'),
                            'lat': leg.get('to', {}).get('lat'),
                            'lon': leg.get('to', {}).get('lon')
                        },
                        'distance': leg.get('distance', 0),
                        'duration': leg.get('duration', 0),
                        'route': leg.get('route', ''),
                        'headsign': leg.get('headsign', ''),
                    }
                    
                    # Add coordinates if available
                    if 'legGeometry' in leg and 'points' in leg['legGeometry']:
                        leg_info['geometry'] = leg['legGeometry']['points']
                    
                    route_info['legs'].append(leg_info)
                
                # Add all itineraries for comparison
                route_info['all_itineraries'] = []
                for itinerary in itineraries:
                    route_info['all_itineraries'].append({
                        'duration': itinerary.get('duration', 0),
                        'distance': sum(leg.get('distance', 0) for leg in itinerary.get('legs', [])),
                        'transfers': itinerary.get('transfers', 0),
                        'walkDistance': itinerary.get('walkDistance', 0)
                    })
                
                return route_info
            else:
                print(f"No itineraries in API response: {data}")
                return None
        else:
            print(f"BKK API error: Status code {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("BKK API request timeout")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error while calling BKK API: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in BKK route calculation: {e}")
        return None


def get_route_with_nearest_stops(start_coords, end_coords):
    """
    Calculate a public transport route using nearest BKK stops.
    
    This function first finds the nearest BKK stops to the start and end coordinates,
    then calculates the route between them.
    
    Args:
        start_coords: Tuple of (latitude, longitude) for start point
        end_coords: Tuple of (latitude, longitude) for end point
    
    Returns:
        Dictionary with route information including nearest stops, or None if error
    """
    try:
        start_lat, start_lon = start_coords
        end_lat, end_lon = end_coords
        
        # Find nearest BKK stops
        start_stop = Location.find_nearest_bkk_stop(start_lat, start_lon)
        end_stop = Location.find_nearest_bkk_stop(end_lat, end_lon)
        
        if not start_stop or not end_stop:
            print("Could not find nearest BKK stops")
            return None
        
        # Calculate route using BKK API
        route = get_route(start_coords, end_coords)
        
        if route:
            # Add information about nearest stops
            route['nearest_stops'] = {
                'start': start_stop,
                'end': end_stop
            }
        
        return route
        
    except Exception as e:
        print(f"Error in get_route_with_nearest_stops: {e}")
        return None
