from flask import Blueprint, jsonify, request
from backend.statics.localisation import Location

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
