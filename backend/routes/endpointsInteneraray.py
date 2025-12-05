from flask import Blueprint, jsonify, request
from backend.statics.itinerary import Itinerary

itinerary_bp = Blueprint('itinerary', __name__)

@itinerary_bp.route('/api/route', methods=['POST'])
def calculate_bike_route():
    try:
        data = request.json
        route = Itinerary.get_bike_route(
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

@itinerary_bp. route('/api/route-with-stations', methods=['POST'])
def route_with_stations():
    try:
        data = request.json
        start_coords = (float(data.get('start_lat')), float(data.get('start_lon')))
        end_coords = (float(data. get('end_lat')), float(data.get('end_lon')))

        result = Itinerary.get_bike_route_with_bubi(start_coords, end_coords)

        if result:
            return jsonify({
                'success': True,
                **result
            })
        else:
            return jsonify({'success': False, 'error': 'Stations not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@itinerary_bp.route('/api/route', methods=['POST'])
def calculate_car_route():
    try:
        data = request.json
        route = Itinerary.get_car_route(
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
