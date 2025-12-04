from flask import Blueprint, jsonify, request
from backend.entities.services.WeatherService import (
    create_weather,
    get_weather_by_id,
    get_all_weather,
    get_weather_by_location,
    get_weather_by_date_range,
    count_weather_records,
    update_weather,
    delete_weather
)
from backend.statics.weather.Weather import get_weather
from backend.statics.localisation.UserLocalisation import get_my_coordinates
from datetime import datetime

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/api/weather', methods=['POST'])
def create_weather_record():
    """Create a new weather record"""
    try:
        data = request.json
        date = data.get('date')
        position_lat = data.get('position_lat')
        position_lon = data.get('position_lon')
        temperature = data.get('temperature')
        precipitation = data.get('precipitation')
        wind_speed = data.get('windSpeed')

        if not date or position_lat is None or position_lon is None:
            return jsonify({
                'success': False,
                'error': 'date, position_lat, and position_lon are required'
            }), 400

        weather_id = create_weather(
            date=date,
            position_lat=position_lat,
            position_lon=position_lon,
            temperature=temperature,
            precipitation=precipitation,
            wind_speed=wind_speed
        )

        if weather_id:
            return jsonify({
                'success': True,
                'message': 'Weather record created successfully',
                'weather_id': weather_id
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create weather record'
            }), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather', methods=['GET'])
def get_all_weather_records():
    """Get all weather records with pagination"""
    try:
        limit = request.args.get('limit', default=100, type=int)
        offset = request.args.get('offset', default=0, type=int)

        weather_records = get_all_weather(limit=limit, offset=offset)
        total = count_weather_records()

        return jsonify({
            'success': True,
            'weather': weather_records,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/<int:weather_id>', methods=['GET'])
def get_weather_by_id_route(weather_id):
    """Get a weather record by ID"""
    try:
        weather = get_weather_by_id(weather_id)

        if weather:
            return jsonify({
                'success': True,
                'weather': weather
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Weather record not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/location', methods=['GET'])
def get_weather_by_location_route():
    """Get weather records by location"""
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        limit = request.args.get('limit', default=10, type=int)

        if lat is None or lon is None:
            return jsonify({
                'success': False,
                'error': 'lat and lon parameters are required'
            }), 400

        weather_records = get_weather_by_location(lat, lon, limit)

        return jsonify({
            'success': True,
            'weather': weather_records,
            'count': len(weather_records)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/<int:weather_id>', methods=['PUT', 'PATCH'])
def update_weather_route(weather_id):
    """Update a weather record"""
    try:
        data = request.json
        date = data.get('date')
        temperature = data.get('temperature')
        precipitation = data.get('precipitation')
        wind_speed = data.get('windSpeed')
        position_lat = data.get('position_lat')
        position_lon = data.get('position_lon')

        # Check if weather record exists
        weather = get_weather_by_id(weather_id)
        if not weather:
            return jsonify({
                'success': False,
                'error': 'Weather record not found'
            }), 404

        success = update_weather(
            weather_id=weather_id,
            date=date,
            temperature=temperature,
            precipitation=precipitation,
            wind_speed=wind_speed,
            position_lat=position_lat,
            position_lon=position_lon
        )

        if success:
            updated_weather = get_weather_by_id(weather_id)
            return jsonify({
                'success': True,
                'message': 'Weather record updated successfully',
                'weather': updated_weather
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Update failed'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/<int:weather_id>', methods=['DELETE'])
def delete_weather_route(weather_id):
    """Delete a weather record"""
    try:
        success = delete_weather(weather_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Weather record deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Weather record not found'
            }), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/count', methods=['GET'])
def count_weather():
    """Get total count of weather records"""
    try:
        count = count_weather_records()

        return jsonify({
            'success': True,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/current', methods=['GET'])
def get_current_weather():
    """Fetch current weather from external API and save to database"""
    try:
        # Get current weather from external API
        weather_data = get_weather()
        
        if not weather_data:
            return jsonify({
                'success': False,
                'error': 'Failed to fetch weather data'
            }), 500
        
        # Get current coordinates
        lat, lon = get_my_coordinates()
        
        # Save to database
        weather_id = create_weather(
            date=datetime.now(),
            position_lat=lat,
            position_lon=lon,
            temperature=weather_data.get('temperature'),
            precipitation=weather_data.get('precipitation'),
            wind_speed=weather_data.get('wind_speed')
        )
        
        return jsonify({
            'success': True,
            'weather': {
                'id': weather_id,
                'temperature': weather_data.get('temperature'),
                'precipitation': weather_data.get('precipitation'),
                'wind_speed': weather_data.get('wind_speed'),
                'position_lat': lat,
                'position_lon': lon
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@weather_bp.route('/api/weather/latest', methods=['GET'])
def get_latest_weather():
    """Get the most recent weather record from database"""
    try:
        # Get all weather records ordered by date (most recent first)
        weather_records = get_all_weather(limit=1, offset=0)
        
        if not weather_records:
            return jsonify({
                'success': False,
                'error': 'No weather records found'
            }), 404
        
        latest_weather = weather_records[0]
        
        return jsonify({
            'success': True,
            'weather': latest_weather
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500