from flask import Blueprint, jsonify, request
from backend.entities.services.UserService import(
    create_user,
    get_user_by_id as service_get_user_by_id,
    update_user as service_update_user,
    update_password as service_update_password,
    delete_user as service_delete_user
)

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['POST'])
def new_user():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400

        user_id = create_user(name, email, password)
        if user_id:
            return jsonify({'success': True, 'message': 'User created successfully', 'user_id': user_id}), 201
        else:
            return jsonify({'success': False, 'error': 'This email already exists'}), 409

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_endpoint(user_id):
    """Retrieves a user by their ID"""
    try:
        user = service_get_user_by_id(user_id)

        if user:
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user_endpoint(user_id):
    """Updates a user"""
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')

        # Check if the user exists
        user = service_get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        success = service_update_user(
            user_id,
            name=name,
            email=email,
            password=password,
            phone=phone
        )

        if success:
            # Get the updated user
            updated_user = service_get_user_by_id(user_id)
            return jsonify({
                'success': True,
                'message': 'User updated successfully',
                'user': updated_user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Update failed (email already in use?)'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>/password', methods=['PUT'])
def update_password_endpoint(user_id):
    """Updates only the password"""
    try:
        data = request.json
        new_password = data.get('password')

        if not new_password:
            return jsonify({
                'success': False,
                'error': 'New password is required'
            }), 400

        success = service_update_password(user_id, new_password)

        if success:
            return jsonify({
                'success': True,
                'message': 'Password updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user_endpoint(user_id):
    """Deletes a user"""
    try:
        success = service_delete_user(user_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

