from flask import Blueprint, jsonify, request, render_template
from backend.entities.services.UserService import(
    get_user_by_email
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    return render_template('login.html')

@auth_bp.route('/signup')
def signup_page():
    return render_template('signup.html')

@auth_bp.route('/account')
def account_page():
    return render_template('account.html')

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400

        user = get_user_by_email(email)
        if not user:
            return jsonify({'success': False, 'error': 'Incorrect email or password'}), 401

        if user['password'] == password:
            user_safe = {k: v for k, v in user.items() if k != 'password'}
            return jsonify({'success': True, 'message': 'Login successful', 'user': user_safe}), 200
        else:
            return jsonify({'success': False, 'error': 'Incorrect email or password'}), 401

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500