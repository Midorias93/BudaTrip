from flask import Blueprint, jsonify, request
from backend.entities.services.PassesService import (
    create_pass,
    get_pass_by_id,
    get_all_passes,
    get_passes_by_user,
    get_passes_by_type,
    count_passes,
    count_passes_by_user,
    update_pass,
    delete_pass,
    delete_passes_by_user
)

passes_bp = Blueprint('passes', __name__)

@passes_bp.route('/api/passes', methods=['POST'])
def create_pass_route():
    """Create a new pass"""
    try:
        data = request.json
        pass_type = data.get('type')
        price = data.get('price')
        user_id = data.get('user_id')

        if not pass_type or price is None or not user_id:
            return jsonify({
                'success': False,
                'error': 'type, price, and user_id are required'
            }), 400

        pass_id = create_pass(
            pass_type=pass_type,
            price=price,
            user_id=user_id
        )

        if pass_id:
            return jsonify({
                'success': True,
                'message': 'Pass created successfully',
                'pass_id': pass_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create pass'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes', methods=['GET'])
def get_all_passes_route():
    """Get all passes with pagination"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)

        passes = get_all_passes(limit=limit, offset=offset)
        total = count_passes()

        return jsonify({
            'success': True,
            'passes': passes,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes/<int:pass_id>', methods=['GET'])
def get_pass_route(pass_id):
    """Get a pass by ID"""
    try:
        transport_pass = get_pass_by_id(pass_id)

        if transport_pass:
            return jsonify({
                'success': True,
                'pass': transport_pass
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Pass not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes/user/<int:user_id>', methods=['GET'])
def get_passes_by_user_route(user_id):
    """Get all passes for a specific user"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        passes = get_passes_by_user(user_id, limit)
        count = count_passes_by_user(user_id)

        return jsonify({
            'success': True,
            'passes': passes,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes/type/<pass_type>', methods=['GET'])
def get_passes_by_type_route(pass_type):
    """Get all passes of a specific type"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        passes = get_passes_by_type(pass_type, limit)

        return jsonify({
            'success': True,
            'passes': passes,
            'count': len(passes)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes/<int:pass_id>', methods=['PUT', 'PATCH'])
def update_pass_route(pass_id):
    """Update a pass"""
    try:
        data = request.json
        pass_type = data.get('type')
        price = data.get('price')

        # Check if pass exists
        transport_pass = get_pass_by_id(pass_id)
        if not transport_pass:
            return jsonify({
                'success': False,
                'error': 'Pass not found'
            }), 404

        success = update_pass(
            pass_id=pass_id,
            pass_type=pass_type,
            price=price
        )

        if success:
            updated_pass = get_pass_by_id(pass_id)
            return jsonify({
                'success': True,
                'message': 'Pass updated successfully',
                'pass': updated_pass
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Update failed'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes/<int:pass_id>', methods=['DELETE'])
def delete_pass_route(pass_id):
    """Delete a pass"""
    try:
        success = delete_pass(pass_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Pass deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Pass not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes/user/<int:user_id>', methods=['DELETE'])
def delete_passes_by_user_route(user_id):
    """Delete all passes for a user"""
    try:
        count = delete_passes_by_user(user_id)

        return jsonify({
            'success': True,
            'message': f'{count} pass(es) deleted successfully',
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@passes_bp.route('/api/passes/count', methods=['GET'])
def count_passes_route():
    """Get total count of passes"""
    try:
        count = count_passes()

        return jsonify({
            'success': True,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
