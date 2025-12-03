from flask import Blueprint, jsonify, request
from Localisation import Itinerary, Location

location_bp = Blueprint('location', __name__)

@location_bp.route('/api/my-location', methods=['GET'])
def my_location():
    try:
        coords = Location.get_my_coordinates()
        return jsonify({'success': True, 'latitude': coords[0], 'longitude': coords[1]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@location_bp.route('/api/stations', methods=['GET'])
def get_stations():
    try:
        stations = Location.bubi_location()
        stations_list = [
            {'name': name, 'lat': coords[0], 'lon': coords[1]}
            for name, coords in stations.items()
        ]
        return jsonify({'success': True, 'stations': stations_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@location_bp.route('/api/geocode', methods=['POST'])
def geocode():
    try:
        data = request.json
        address = data.get('address')
        result = Location.get_coordinates(address)

        if isinstance(result, dict) and 'latitude' in result:
            return jsonify({
                'success': True,
                'address': result['address'],
                'latitude': result['latitude'],
                'longitude': result['longitude']
            })
        else:
            return jsonify({'success': False, 'error': 'Address not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@location_bp.route('/api/nearest-station', methods=['POST'])
def nearest_station():
    try:
        data = request.json
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))

        stations = Location.bubi_location()
        nearest = Location.find_nearest_station((lat, lon), stations)

        if nearest:
            name, coords, distance = nearest
            return jsonify({
                'success': True,
                'station': {'name': name, 'lat': coords[0], 'lon': coords[1], 'distance': round(distance, 2)}
            })
        else:
            return jsonify({'success': False, 'error': 'No station found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@location_bp.route('/api/route', methods=['POST'])
def calculate_route():
    try:
        data = request.json
        route = Itinerary.get_route(
            (float(data.get('start_lat')), float(data.get('start_lon'))),
            (float(data.get('end_lat')), float(data.get('end_lon'))),
            mode=data.get('mode', 'bike')
        )

        if route:
            return jsonify({
                'success': True,
                'route': {
                    'coordinates': route['coordinates'],
                    'distance': route['distance'],
                    'duration': route['duration']
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to calculate route'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@location_bp.route('/api/route-with-stations', methods=['POST'])
def route_with_stations():
    try:
        data = request.json
        start_lat = float(data.get('start_lat'))
        start_lon = float(data.get('start_lon'))
        end_lat = float(data.get('end_lat'))
        end_lon = float(data.get('end_lon'))

        stations = Location.bubi_location()
        start_station = Location.find_nearest_station((start_lat, start_lon), stations)
        end_station = Location.find_nearest_station((end_lat, end_lon), stations)

        if not start_station or not end_station:
            return jsonify({'success': False, 'error': 'Stations not found'}), 404

        start_station_name, start_station_coords, start_distance = start_station
        end_station_name, end_station_coords, end_distance = end_station

        walk_to_start = Itinerary.get_route((start_lat, start_lon), start_station_coords, mode='foot')
        bike_route = Itinerary.get_route(start_station_coords, end_station_coords, mode='bike')
        walk_from_end = Itinerary.get_route(end_station_coords, (end_lat, end_lon), mode='foot')

        return jsonify({
            'success': True,
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
            'total_distance': (
                (walk_to_start['distance'] if walk_to_start else 0) +
                (bike_route['distance'] if bike_route else 0) +
                (walk_from_end['distance'] if walk_from_end else 0)
            ),
            'total_duration': (
                (walk_to_start['duration'] if walk_to_start else 0) +
                (bike_route['duration'] if bike_route else 0) +
                (walk_from_end['duration'] if walk_from_end else 0)
            )
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500