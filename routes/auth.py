from flask import Blueprint, jsonify, request, render_template
from DataBase import Users
import asyncio

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
            return jsonify({'success': False, 'error': 'Email et password requis'}), 400

        user = asyncio.run(Users.get_user_by_email(email))
        if not user:
            return jsonify({'success': False, 'error': 'Email ou mot de passe incorrect'}), 401

        if user['password'] == password:
            user_safe = {k: v for k, v in user.items() if k != 'password'}
            return jsonify({'success': True, 'message': 'Connexion réussie', 'user': user_safe}), 200
        else:
            return jsonify({'success': False, 'error': 'Email ou mot de passe incorrect'}), 401

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.json
        nom = data.get('nom')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email et password requis'}), 400

        exists = asyncio.run(Users.user_exists(email))
        if exists:
            return jsonify({'success': False, 'error': 'Cet email est déjà utilisé'}), 409

        user_id = asyncio.run(Users.create_user(nom, email, password))
        if user_id:
            user = asyncio.run(Users.get_user_by_id(user_id))
            user_safe = {k: v for k, v in user.items() if k != 'password'}
            return jsonify({'success': True, 'message': 'Inscription réussie', 'user': user_safe}), 201
        else:
            return jsonify({'success': False, 'error': 'Erreur lors de l\'inscription'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500