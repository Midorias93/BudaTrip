from flask import Blueprint, jsonify, request
from backend.entities.services.TravelsService import (
    create_travel,
    get_travel_by_id,
    get_all_travels,
    get_travels_by_user,
    get_travels_by_transport_type,
    count_travels,
    count_travels_by_user,
    get_total_distance_by_user,
    get_total_co2_by_user,
    get_total_cost_by_user,
    get_distance_by_transport,
    get_co2_by_transport,
    get_cost_by_transport,
    update_travel,
    delete_travel,
    delete_travels_by_user
)
from backend.entities.models.PassesModel import Pass

travels_bp = Blueprint('travels', __name__)

@travels_bp.route('/api/travels', methods=['POST'])
def create_travel_route():
    """Create a new travel record"""
    try:
        data = request.json
        user_id = data.get('user_id')
        duration = data.get('duration')
        distance = data.get('distance')
        start_lat = data.get('start_lat')
        start_lon = data.get('start_lon')
        end_lat = data.get('end_lat')
        end_lon = data.get('end_lon')
        transport_type = data.get('transportType')
        cost = data.get('cost')
        co2_emissions = data.get('CO2Emissions')
        weather_id = data.get('weather_id')

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400

        travel_id = create_travel(
            user_id=user_id,
            duration=duration,
            distance=distance,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            transport_type=transport_type,
            cost=cost,
            co2_emissions=co2_emissions,
            weather_id=weather_id,
        )

        if travel_id:
            return jsonify({
                'success': True,
                'message': 'Travel record created successfully',
                'travel_id': travel_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create travel record'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels', methods=['GET'])
def get_all_travels_route():
    """Get all travel records with pagination"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)

        travels = get_all_travels(limit=limit, offset=offset)
        total = count_travels()

        return jsonify({
            'success': True,
            'travels': travels,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/<int:travel_id>', methods=['GET'])
def get_travel_route(travel_id):
    """Get a travel record by ID"""
    try:
        travel = get_travel_by_id(travel_id)

        if travel:
            return jsonify({
                'success': True,
                'travel': travel
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Travel record not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/user/<int:user_id>', methods=['GET'])
def get_travels_by_user_route(user_id):
    """Get all travels for a specific user"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        travels = get_travels_by_user(user_id, limit, offset)
        count = count_travels_by_user(user_id)

        return jsonify({
            'success': True,
            'travels': travels,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/transport-type/<transport_type>', methods=['GET'])
def get_travels_by_transport_type_route(transport_type):
    """Get all travels by transport type"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        travels = get_travels_by_transport_type(transport_type, limit)

        return jsonify({
            'success': True,
            'travels': travels,
            'count': len(travels)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/user/<int:user_id>/stats', methods=['GET'])
def get_user_travel_stats(user_id):
    """
    Get comprehensive travel statistics for a user.
    
    Returns:
        Statistics including:
        - Total and per-transport distances
        - CO2 emissions (total and by transport)
        - Costs (total and by transport, including pass info)
    """
    try:
        # Get total statistics
        total_distance = get_total_distance_by_user(user_id)
        total_co2 = get_total_co2_by_user(user_id)
        total_cost = get_total_cost_by_user(user_id)
        travel_count = count_travels_by_user(user_id)
        
        # Get statistics by transport type
        distances_by_transport = get_distance_by_transport(user_id)
        co2_by_transport = get_co2_by_transport(user_id)
        cost_by_transport = get_cost_by_transport(user_id)

        # Get user passes
        user_passes = list(Pass.select().where(Pass.user_id == user_id))
        pass_types = [p.type for p in user_passes]

        return jsonify({
            'success': True,
            'statistics': {
                'user_id': user_id,
                'travel_count': travel_count,
                'distances': {
                    'total': total_distance,
                    'by_transport': distances_by_transport
                },
                'pollution': {
                    'total_co2': total_co2,
                    'by_transport': co2_by_transport
                },
                'costs': {
                    'total_cost': total_cost,
                    'by_transport': cost_by_transport,
                    'passes': pass_types
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/<int:travel_id>', methods=['PUT', 'PATCH'])
def update_travel_route(travel_id):
    """Update a travel record"""
    try:
        data = request.json
        duration = data.get('duration')
        distance = data.get('distance')
        start_lat = data.get('start_lat')
        start_lon = data.get('start_lon')
        end_lat = data.get('end_lat')
        end_lon = data.get('end_lon')
        transport_type = data.get('transportType')
        cost = data.get('cost')
        co2_emissions = data.get('CO2Emissions')
        weather_id = data.get('weather_id')

        # Check if travel record exists
        travel = get_travel_by_id(travel_id)
        if not travel:
            return jsonify({
                'success': False,
                'error': 'Travel record not found'
            }), 404

        success = update_travel(
            travel_id=travel_id,
            duration=duration,
            distance=distance,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            transport_type=transport_type,
            cost=cost,
            co2_emissions=co2_emissions,
            weather_id=weather_id,
        )

        if success:
            updated_travel = get_travel_by_id(travel_id)
            return jsonify({
                'success': True,
                'message': 'Travel record updated successfully',
                'travel': updated_travel
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Update failed'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/<int:travel_id>', methods=['DELETE'])
def delete_travel_route(travel_id):
    """Delete a travel record"""
    try:
        success = delete_travel(travel_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Travel record deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Travel record not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/user/<int:user_id>', methods=['DELETE'])
def delete_travels_by_user_route(user_id):
    """Delete all travel records for a user"""
    try:
        count = delete_travels_by_user(user_id)

        return jsonify({
            'success': True,
            'message': f'{count} travel record(s) deleted successfully',
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@travels_bp.route('/api/travels/count', methods=['GET'])
def count_travels_route():
    """Get total count of travel records"""
    try:
        count = count_travels()

        return jsonify({
            'success': True,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
