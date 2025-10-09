from flask import Flask, render_template, request, jsonify
import Location
import Itinerary
import folium
import json

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/my-location', methods=['GET'])
def my_location():
    """Récupère la position de l'utilisateur"""
    try:
        coords = Location.get_my_coordinates()
        return jsonify({
            'success': True,
            'latitude': coords[0],
            'longitude': coords[1]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Récupère toutes les stations Bubi"""
    try:
        stations = Location.bubi_location()
        # Convertir en format JSON-friendly
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
    """Convertit une adresse en coordonnées"""
    try:
        data = request.json
        address = data.get('address')

        result = Location.get_coordinates(address)

        if isinstance(result, dict) and 'latitude' in result:
            return jsonify({
                'success': True,
                'address': result['adresse'],
                'latitude': result['latitude'],
                'longitude': result['longitude']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Adresse non trouvée'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/nearest-station', methods=['POST'])
def nearest_station():
    """Trouve la station la plus proche"""
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
    """Calcule un itinéraire entre deux points"""
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
    """Calcule un itinéraire en utilisant les stations Bubi"""
    try:
        data = request.json
        start_lat = float(data.get('start_lat'))
        start_lon = float(data.get('start_lon'))
        end_lat = float(data.get('end_lat'))
        end_lon = float(data.get('end_lon'))

        stations = Location.bubi_location()

        # Trouver la station la plus proche du départ
        start_station = Location.find_nearest_station((start_lat, start_lon), stations)
        # Trouver la station la plus proche de l'arrivée
        end_station = Location.find_nearest_station((end_lat, end_lon), stations)

        if not start_station or not end_station:
            return jsonify({
                'success': False,
                'error': 'Stations non trouvées'
            }), 404

        start_station_name, start_station_coords, start_distance = start_station
        end_station_name, end_station_coords, end_distance = end_station

        # Calculer les 3 segments de l'itinéraire
        # 1. Marche jusqu'à la station de départ
        walk_to_start = Itinerary.get_route(
            (start_lat, start_lon),
            start_station_coords,
            mode='foot'
        )

        # 2. Vélo entre les deux stations
        bike_route = Itinerary.get_route(
            start_station_coords,
            end_station_coords,
            mode='bike'
        )

        # 3. Marche depuis la station d'arrivée
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)
