from flask import Blueprint, jsonify
from Localisation import Location
import psycopg2
from config import Config

def get_bkk_db_conn():
    return psycopg2.connect(
        host=Config.POSTGRES_HOST,
        port=Config.POSTGRES_PORT,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        dbname=Config.POSTGRES_DB,
    )
bkk_bp = Blueprint('bkk', __name__)

@bkk_bp.route("/api/bkk/nearest-stop", methods=["GET"])
def api_bkk_nearest_stop():
    lat, lon = Location.get_my_coordinates()
    conn = get_bkk_db_conn()
    try:
        stop = Location.find_nearest_bkk_stop(conn, lat, lon)
    finally:
        conn.close()

    if not stop:
        return jsonify({"error": "No stop found in database"}), 404
    return jsonify(stop), 200