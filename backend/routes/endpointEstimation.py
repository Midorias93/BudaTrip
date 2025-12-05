from flask import Blueprint, jsonify
from backend.entities.services.TravelsService import (
    get_total_distance_by_user,
    get_total_co2_by_user,
    get_total_cost_by_user,
    get_distance_by_transport,
    get_co2_by_transport,
    get_cost_by_transport,
    count_travels_by_user
)
from backend.entities.models.PassesModel import Pass
from backend.entities.models.UserModel import User

estimation_bp = Blueprint('estimation', __name__)


@estimation_bp.route('/api/estimation/statistics/<int:user_id>', methods=['GET'])
def get_statistics(user_id):
    """
    Get comprehensive statistics for a user.

    Returns combined data including:
    - Total and per-transport distances
    - CO2 emissions (total and by transport)
    - Costs (total and by transport, including pass info)
    
    This endpoint redirects to the travel stats endpoint logic for consistency.
    """
    try:
        # Verify user exists
        user_exists = User.select().where(User.id == user_id).exists()
        if not user_exists:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get total statistics
        total_distance = get_total_distance_by_user(user_id)
        total_co2 = get_total_co2_by_user(user_id)
        total_cost = get_total_cost_by_user(user_id)
        
        # Get statistics by transport type
        distances_by_transport = get_distance_by_transport(user_id)
        co2_by_transport = get_co2_by_transport(user_id)
        cost_by_transport = get_cost_by_transport(user_id)
        
        # Get user passes
        user_passes = list(Pass.select().where(Pass.user_id == user_id))
        pass_types = [p.type for p in user_passes]

        statistics = {
            'user_id': user_id,
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

        return jsonify({
            'success': True,
            'statistics': statistics
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500