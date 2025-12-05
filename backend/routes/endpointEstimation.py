from flask import Blueprint, jsonify, request
from backend.statics.estimation import (
    get_user_distance_by_transport,
    get_user_pollution,
    get_user_cost,
    get_user_statistics
)

estimation_bp = Blueprint('estimation', __name__)


@estimation_bp.route('/api/estimation/distance/<int:user_id>', methods=['GET'])
def get_distance_by_transport(user_id):
    """
    Get total distance traveled by a user for each transport type.

    Returns distance in meters for each transport type (CAR, TRANSPORT, BUBI, BIKE, WALK)
    """
    try:
        distances = get_user_distance_by_transport(user_id)

        if distances is not None:
            return jsonify({
                'success': True,
                'user_id': user_id,
                'distances': distances
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Unable to retrieve distance data'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@estimation_bp.route('/api/estimation/pollution/<int:user_id>', methods=['GET'])
def get_pollution(user_id):
    """
    Get CO2 emissions produced by a user's travels.

    Returns total CO2 in grams and breakdown by transport type.
    CO2 rates: CAR=180g/km, TRANSPORT=2g/km, BUBI/BIKE/WALK=0g/km
    """
    try:
        pollution = get_user_pollution(user_id)

        return jsonify({
            'success': True,
            'user_id': user_id,
            'pollution': pollution
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@estimation_bp.route('/api/estimation/cost/<int:user_id>', methods=['GET'])
def get_cost(user_id):
    """
    Get total travel costs for a user in Forint.

    Cost rules:
    - CAR: 250 Forint per kilometer
    - TRANSPORT: Free with BKK pass, otherwise 250 Forint per travel
    - BUBI: Free with BUBI pass, otherwise 250 Forint per travel
    - BIKE/WALK: Always free
    """
    try:
        costs = get_user_cost(user_id)

        return jsonify({
            'success': True,
            'user_id': user_id,
            'costs': costs
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@estimation_bp.route('/api/estimation/statistics/<int:user_id>', methods=['GET'])
def get_statistics(user_id):
    """
    Get comprehensive statistics for a user.

    Returns combined data including:
    - Total and per-transport distances
    - CO2 emissions (total and by transport)
    - Costs (total and by transport, including pass info)
    """
    try:
        statistics = get_user_statistics(user_id)

        if statistics:
            return jsonify({
                'success': True,
                'statistics': statistics
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500