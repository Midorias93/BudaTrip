from flask import Flask, render_template, request, jsonify
from AppFunctions import Itinerary, Location, Weather
from BudaTripDB import UserFunctions
import asyncio

app = Flask(__name__)

print("Dossiers static:", app.static_folder)

# ==================================================
# ==================== END POINT ===================
# ==================================================

# ==================================================
# ==================== DEFAULT ROUTES ==============
# ==================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/account')
def account_page():
    return render_template('account.html')


# ==================================================
# ==================== EXEMPLE =====================
# ==================================================

@app.route('/hello-world', methods=['GET'])
def hello_world():
    return jsonify({'hello': 'world'}), 200



# ==================================================
# ==================== LOCATION ====================
# ==================================================

@app.route('/api/my-location', methods=['GET'])
def my_location():
    try:
        coords = Location.get_my_coordinates()
        return jsonify({
            'success': True,
            'latitude': coords[0],
            'longitude': coords[1]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test-static')
def test_static():
    import os
    static_path = os.path.join(app.root_path, 'static', 'css', 'style.css')
    exists = os.path.exists(static_path)
    return f"Fichier existe: {exists}<br>Chemin: {static_path}"


@app.route('/api/stations', methods=['GET'])
def get_stations():
    try:
        stations = Location.bubi_location()
        stations_list = [
            {
                'name': name,
                'lat': coords[0],
                'lon': coords[1]
            }
            for name, coords in stations.items()
        ]
        return jsonify({
            'success': True,
            'stations': stations_list
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/geocode', methods=['POST'])
def geocode():
    try:
        data = request.json
        address = data.get('address')

        result = Location.get_coordinates(address)

        if isinstance(result, dict) and 'latitude' in result:
            return jsonify({
                'success': True,
                'address': result['address'],
                'latitude': result['latitude'],
                'longitude': result['longitude']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Address not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/nearest-station', methods=['POST'])
def nearest_station():
    try:
        data = request.json
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))

        stations = Location.bubi_location()
        nearest = Location.find_nearest_station((lat, lon), stations)

        if nearest:
            name, coords, distance = nearest
            return jsonify({
                'success': True,
                'station': {
                    'name': name,
                    'lat': coords[0],
                    'lon': coords[1],
                    'distance': round(distance, 2)
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Aucune station trouvée'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/route', methods=['POST'])
def calculate_route():
    try:
        data = request.json
        start_lat = float(data.get('start_lat'))
        start_lon = float(data.get('start_lon'))
        end_lat = float(data.get('end_lat'))
        end_lon = float(data.get('end_lon'))
        mode = data.get('mode', 'bike')

        route = Itinerary.get_route(
            (start_lat, start_lon),
            (end_lat, end_lon),
            mode=mode
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
            return jsonify({
                'success': False,
                'error': 'Impossible de calculer l\'itinéraire'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/route-with-stations', methods=['POST'])
def route_with_stations():
    try:
        data = request.json
        start_lat = float(data.get('start_lat'))
        start_lon = float(data.get('start_lon'))
        end_lat = float(data.get('end_lat'))
        end_lon = float(data.get('end_lon'))

        stations = Location.bubi_location()

        start_station = Location.find_nearest_station((start_lat, start_lon), stations)

        end_station = Location.find_nearest_station((end_lat, end_lon), stations)

        if not start_station or not end_station:
            return jsonify({
                'success': False,
                'error': 'Stations non trouvées'
            }), 404

        start_station_name, start_station_coords, start_distance = start_station
        end_station_name, end_station_coords, end_distance = end_station

        walk_to_start = Itinerary.get_route(
            (start_lat, start_lon),
            start_station_coords,
            mode='foot'
        )

        bike_route = Itinerary.get_route(
            start_station_coords,
            end_station_coords,
            mode='bike'
        )

        walk_from_end = Itinerary.get_route(
            end_station_coords,
            (end_lat, end_lon),
            mode='foot'
        )

        return jsonify({
            'success': True,
            'start_station': {
                'name': start_station_name,
                'lat': start_station_coords[0],
                'lon': start_station_coords[1],
                'distance': round(start_distance, 2)
            },
            'end_station': {
                'name': end_station_name,
                'lat': end_station_coords[0],
                'lon': end_station_coords[1],
                'distance': round(end_distance, 2)
            },
            'routes': {
                'walk_to_start': walk_to_start,
                'bike': bike_route,
                'walk_from_end': walk_from_end
            },
            'total_distance': (
                    (walk_to_start['distance'] if walk_to_start else 0) +
                    (bike_route['distance'] if bike_route else 0) +
                    (walk_from_end['distance'] if walk_from_end else 0)
            ),
            'total_duration': (
                    (walk_to_start['duration'] if walk_to_start else 0) +
                    (bike_route['duration'] if bike_route else 0) +
                    (walk_from_end['duration'] if walk_from_end else 0)
            )
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/weather', methods=['GET'])
def get_weather():
    try:
        weather = Weather.get_weather()
        if weather:
            return jsonify({
                'success': True,
                'weather': weather
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Impossible to get weather data'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================================================
# ==================== DataBase ====================
# ==================================================

# ==================== ENDPOINTS UTILISATEURS ====================

@app.route('/api/users', methods=['POST'])
def create_user():
    """Crée un nouvel utilisateur"""
    try:
        data = request.json
        nom = data.get('nom')
        email = data.get('email')
        password = data.get('password')

        # Validation
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email et password sont obligatoires'
            }), 400

        # Créer l'utilisateur
        user_id = asyncio.run(UserFunctions.create_user(nom, email, password))

        if user_id:
            return jsonify({
                'success': True,
                'message': 'Utilisateur créé avec succès',
                'user_id': user_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Cet email existe déjà'
            }), 409

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Récupère tous les utilisateurs avec pagination"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)

        users = asyncio.run(UserFunctions.get_all_users(limit=limit, offset=offset))
        total = asyncio.run(UserFunctions.count_users())

        return jsonify({
            'success': True,
            'users': users,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Récupère un utilisateur par son ID"""
    try:
        user = asyncio.run(UserFunctions.get_user_by_id(user_id))

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


@app.route('/api/users/email/<email>', methods=['GET'])
def get_user_by_email(email):
    """Récupère un utilisateur par son email"""
    try:
        user = asyncio.run(UserFunctions.get_user_by_email(email))

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


@app.route('/api/users/search', methods=['GET'])
def search_users():
    """Recherche des utilisateurs par nom"""
    try:
        query = request.args.get('q', '')

        if not query:
            return jsonify({
                'success': False,
                'error': 'Paramètre de recherche manquant (q)'
            }), 400

        users = asyncio.run(UserFunctions.search_users_by_name(query))

        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/users/<int:user_id>', methods=['PUT', 'PATCH'])
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
        user = asyncio.run(UserFunctions.get_user_by_id(user_id))
        if not user:
            return jsonify({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }), 404

        success = asyncio.run(UserFunctions.update_user(
            user_id,
            nom=nom,
            email=email,
            password=password,
            phone = phone
        ))

        if success:
            # Récupérer l'utilisateur mis à jour
            updated_user = asyncio.run(UserFunctions.get_user_by_id(user_id))
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


@app.route('/api/users/<int:user_id>/password', methods=['PUT'])
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

        success = asyncio.run(UserFunctions.update_password(user_id, new_password))

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


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Supprime un utilisateur"""
    try:
        success = asyncio.run(UserFunctions.delete_user(user_id))

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


@app.route('/api/users/email/<email>', methods=['DELETE'])
def delete_user_by_email(email):
    """Supprime un utilisateur par email"""
    try:
        success = asyncio.run(UserFunctions.delete_user_by_email(email))

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


@app.route('/api/users/check-email', methods=['POST'])
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

        exists = asyncio.run(UserFunctions.user_exists(email))

        return jsonify({
            'success': True,
            'exists': exists
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/users/count', methods=['GET'])
def count_users():
    """Compte le nombre total d'utilisateurs"""
    try:
        count = asyncio.run(UserFunctions.count_users())

        return jsonify({
            'success': True,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authentifie un utilisateur"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email et password requis'
            }), 400

        # Récupérer l'utilisateur
        user = asyncio.run(UserFunctions.get_user_by_email(email))

        if not user:
            return jsonify({
                'success': False,
                'error': 'Email ou mot de passe incorrect'
            }), 401

        # Vérifier le mot de passe (À AMÉLIORER avec bcrypt!)
        if user['password'] == password:
            # Ne pas retourner le mot de passe
            user_safe = {k: v for k, v in user.items() if k != 'password'}
            return jsonify({
                'success': True,
                'message': 'Connexion réussie',
                'user': user_safe
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Email ou mot de passe incorrect'
            }), 401

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Inscrit un nouvel utilisateur"""
    try:
        data = request.json
        nom = data.get('nom')
        email = data.get('email')
        password = data.get('password')

        # Validation
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email et password requis'
            }), 400

        # Vérifier si l'email existe déjà
        exists = asyncio.run(UserFunctions.user_exists(email))
        if exists:
            return jsonify({
                'success': False,
                'error': 'Cet email est déjà utilisé'
            }), 409

        # Créer l'utilisateur (À AMÉLIORER avec bcrypt pour hasher le password!)
        user_id = asyncio.run(UserFunctions.create_user(nom, email, password))

        if user_id:
            user = asyncio.run(UserFunctions.get_user_by_id(user_id))
            user_safe = {k: v for k, v in user.items() if k != 'password'}

            return jsonify({
                'success': True,
                'message': 'Inscription réussie',
                'user': user_safe
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'inscription'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route("/api/bkk/nearest-stop", methods=["GET"])
async def api_bkk_nearest_stop():
    """
    Query params:
      - lat: float (required)
      - lon: float (required)
    Returns JSON with nearest stop.
    """
    lat,lon = Location.get_my_coordinates()
    stop = await Location.find_nearest_bkk_stop(lat, lon)

    if not stop:
        return jsonify({"error": "No stop found in database"}), 404
    return jsonify(stop), 200


async def initDB() :
    try :
        await UserFunctions.create_table()
        await UserFunctions.clear_bkk_table()
        await UserFunctions.fill_bkk_table("BKK/stops.txt")
        return False
    except Exception as e :
        print(f"Erreur de connexion à la base de données : {e}")
        return True


if asyncio.run(initDB()) : exit(1)

# ==================================================
# ==================== MAIN ========================
# ==================================================

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8000)
