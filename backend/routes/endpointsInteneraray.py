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

@itinerary_bp.route('/api/route/car', methods=['POST'])
def calculate_car_route():
    try:
        data = request.json
        route = Itinerary.get_car_route(
            (float(data.get('start_lat')), float(data.get('start_lon'))),
            (float(data.get('end_lat')), float(data.get('end_lon'))),
            mode=data.get('mode', 'driving')
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

@itinerary_bp.route('/api/route/transport', methods=['POST'])
def calculate_transport_route():
    """
    Calculate a public transport route using BKK API.
    
    Expects JSON with:
    - start_lat: Starting latitude
    - start_lon: Starting longitude
    - end_lat: Ending latitude
    - end_lon: Ending longitude
    """
    try:
        data = request.json
        start_coords = (float(data.get('start_lat')), float(data.get('start_lon')))
        end_coords = (float(data.get('end_lat')), float(data.get('end_lon')))
        
        route = Itinerary.get_transport_route(start_coords, end_coords)

        if route:
            return jsonify({
                'success': True,
                'route': route
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to calculate public transport route'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@itinerary_bp.route('/api/route/transport-with-stops', methods=['POST'])
def calculate_transport_route_with_stops():
    """
    Calculate a public transport route with nearest BKK stop information.
    
    Expects JSON with:
    - start_lat: Starting latitude
    - start_lon: Starting longitude
    - end_lat: Ending latitude
    - end_lon: Ending longitude
    """
    try:
        data = request.json
        start_coords = (float(data.get('start_lat')), float(data.get('start_lon')))
        end_coords = (float(data.get('end_lat')), float(data.get('end_lon')))
        
        route = Itinerary.get_transport_route_with_stops(start_coords, end_coords)

        if route:
            return jsonify({
                'success': True,
                'route': route
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to calculate public transport route with stops'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
