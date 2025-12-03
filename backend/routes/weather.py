from flask import Blueprint, jsonify
from Weather import Weather

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/api/weather', methods=['GET'])
def get_weather():
    try:
        weather = Weather.get_weather()
        if weather:
            return jsonify({'success': True, 'weather': weather}), 200
        else:
            return jsonify({'success': False, 'error': 'Unable to get weather data'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500