from flask import Blueprint, jsonify, request

from DataBase.BKK import Stations
from Localisation import Location

bkk_bp = Blueprint('bkk', __name__)

@bkk_bp.route("/api/bkk/nearest-stop", methods=["GET"])
def api_bkk_nearest_stop():
    lat, lon = Location.get_my_coordinates()
    stop = Location.find_nearest_bkk_stop(lat, lon)
    if not stop:
        return jsonify({'error': 'No stop found'}), 404
    return jsonify(stop), 200


@bkk_bp.route("/api/bkk/stations", methods=["GET"])
def get_bkk_stations():
    try:
        stations = Stations.get_all_bkk_stations()

        return jsonify({
            'success': True,
            'stations': stations,
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bkk_bp.route("/api/bkk/stations/<int:stop_id>", methods=["GET"])
def get_bkk_stations_by_stop_id(stop_id):
    station = Stations.get_station_by_stop_id(stop_id)
    if not station:
        return jsonify({"error": "Station not found"}), 404
    return jsonify(station), 200

@bkk_bp.route("/api/bkk/stations/<name>", methods=["GET"])
def get_bkk_stations_by_name(name):
    station = Stations.get_bkk_station_by_name(name)
    if not station:
        return jsonify({"error": "Station not found"}), 404
    return jsonify(station), 200
