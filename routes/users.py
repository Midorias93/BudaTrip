from flask import Blueprint, jsonify, request
from DataBase import Users
import asyncio

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        nom = data.get('nom')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'error': 'Email et password sont obligatoires'}), 400

        user_id = asyncio.run(Users.create_user(nom, email, password))
        if user_id:
            return jsonify({'success': True, 'message': 'Utilisateur créé avec succès', 'user_id': user_id}), 201
        else:
            return jsonify({'success': False, 'error': 'Cet email existe déjà'}), 409

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users', methods=['GET'])
def get_all_users():
    """Récupère tous les utilisateurs avec pagination"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)

        users = asyncio.run(Users.get_all_users(limit=limit, offset=offset))
        total = asyncio.run(Users.count_users())

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
    """Récupère un utilisateur par son ID"""
    try:
        user = asyncio.run(Users.get_user_by_id(user_id))

        if user:
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/email/<email>', methods=['GET'])
def get_user_by_email(email):
    """Récupère un utilisateur par son email"""
    try:
        user = asyncio.run(Users.get_user_by_email(email))

        if user:
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/search', methods=['GET'])
def search_users():
    """Recherche des utilisateurs par nom"""
    try:
        query = request.args.get('q', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Paramètre de recherche manquant (q)'
            }), 400

        users = asyncio.run(Users.search_users_by_name(query))

        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    """Met à jour un utilisateur"""
    try:
        data = request.json
        nom = data.get('nom')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        print(phone)

        # Vérifier si l'utilisateur existe
        user = asyncio.run(Users.get_user_by_id(user_id))
        if not user:
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404

        success = asyncio.run(Users.update_user(
            user_id,
            nom=nom,
            email=email,
            password=password,
            phone = phone
        ))

        if success:
            # Récupérer l'utilisateur mis à jour
            updated_user = asyncio.run(Users.get_user_by_id(user_id))
            return jsonify({
                'success': True,
                'message': 'Utilisateur mis à jour avec succès',
                'user': updated_user
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Échec de la mise à jour (email déjà utilisé ?)'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>/password', methods=['PUT'])
def update_password(user_id):
    """Met à jour uniquement le mot de passe"""
    try:
        data = request.json
        new_password = data.get('password')

        if not new_password:
            return jsonify({
                'success': False,
                'error': 'Le nouveau mot de passe est requis'
            }), 400

        success = asyncio.run(Users.update_password(user_id, new_password))

        if success:
            return jsonify({
                'success': True,
                'message': 'Mot de passe mis à jour avec succès'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Supprime un utilisateur"""
    try:
        success = asyncio.run(Users.delete_user(user_id))

        if success:
            return jsonify({
                'success': True,
                'message': 'Utilisateur supprimé avec succès'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/email/<email>', methods=['DELETE'])
def delete_user_by_email(email):
    """Supprime un utilisateur par email"""
    try:
        success = asyncio.run(Users.delete_user_by_email(email))

        if success:
            return jsonify({
                'success': True,
                'message': 'Utilisateur supprimé avec succès'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/check-email', methods=['POST'])
def check_email():
    """Vérifie si un email existe déjà"""
    try:
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({
                'success': False,
                'error': 'Email requis'
            }), 400

        exists = asyncio.run(Users.user_exists(email))

        return jsonify({
            'success': True,
            'exists': exists
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@users_bp.route('/api/users/count', methods=['GET'])
def count_users():
    """Compte le nombre total d'utilisateurs"""
    try:
        count = asyncio.run(Users.count_users())

        return jsonify({
            'success': True,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

