from flask import Blueprint, jsonify, request
from DataBase import Users

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400

        user_id = Users.create_user(name, email, password)
        if user_id:
            return jsonify({'success': True, 'message': 'User created successfully', 'user_id': user_id}), 201
        else:
            return jsonify({'success': False, 'error': 'This email already exists'}), 409

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users', methods=['GET'])
def get_all_users():
    """Retrieves all users with pagination"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)

        users = Users.get_all_users(limit=limit, offset=offset)
        total = Users.count_users()

        return jsonify({
            'success': True,
            'users': users,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retrieves a user by their ID"""
    try:
        user = Users.get_user_by_id(user_id)

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


@users_bp.route('/api/users/email/<email>', methods=['GET'])
def get_user_by_email(email):
    """Retrieves a user by their email"""
    try:
        user = Users.get_user_by_email(email)

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


@users_bp.route('/api/users/search', methods=['GET'])
def search_users():
    """Search for users by name"""
    try:
        query = request.args.get('q', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Missing search parameter (q)'
            }), 400

        users = Users.search_users_by_name(query)

        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    """Updates a user"""
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        print(phone)

        # Check if the user exists
        user = Users.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        success = Users.update_user(
            user_id,
            name=name,
            email=email,
            password=password,
            phone = phone
        )

        if success:
            # Get the updated user
            updated_user = Users.get_user_by_id(user_id)
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
def update_password(user_id):
    """Updates only the password"""
    try:
        data = request.json
        new_password = data.get('password')

        if not new_password:
            return jsonify({
                'success': False,
                'error': 'New password is required'
            }), 400

        success = Users.update_password(user_id, new_password)

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
def delete_user(user_id):
    """Deletes a user"""
    try:
        success = Users.delete_user(user_id)

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


@users_bp.route('/api/users/email/<email>', methods=['DELETE'])
def delete_user_by_email(email):
    """Deletes a user by email"""
    try:
        success = Users.delete_user_by_email(email)

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


@users_bp.route('/api/users/check-email', methods=['POST'])
def check_email():
    """Checks if an email already exists"""
    try:
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({
                'success': False,
                'error': 'Email required'
            }), 400

        exists = Users.user_exists(email)

        return jsonify({
            'success': True,
            'exists': exists
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/count', methods=['GET'])
def count_users():
    """Counts the total number of users"""
    try:
        count = Users.count_users()

        return jsonify({
            'success': True,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

