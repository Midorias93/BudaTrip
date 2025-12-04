from backend.entities.models.WeatherModel import Weather
from peewee import DoesNotExist
from datetime import datetime


# ==================== CREATE OPERATIONS ====================

def create_weather(date, position_lat, position_lon, temperature=None, precipitation=None, wind_speed=None):
    """Create a new weather record
    
    Args:
        date: Required. Date/time of the weather record.
        position_lat: Required. Latitude of the weather location.
        position_lon: Required. Longitude of the weather location.
        temperature, precipitation, wind_speed: Optional weather attributes.
    
    Returns:
        Weather ID if successful, None otherwise.
    """
    if date is None or position_lat is None or position_lon is None:
        print("Error: date, position_lat, and position_lon are all required")
        return None
        
    try:
        weather = Weather.create(
            date=date,
            temperature=temperature,
            precipitation=precipitation,
            windSpeed=wind_speed,
            position_lat=position_lat,
            position_lon=position_lon
        )
        return weather.id
    except Exception as e:
        print(f"Error creating weather record: {e}")
        return None


# ==================== READ OPERATIONS ====================

def get_weather_by_id(weather_id):
    """Get a weather record by ID"""
    try:
        weather = Weather.get_by_id(weather_id)
        return {
            'id': weather.id,
            'date': weather.date,
            'temperature': weather.temperature,
            'precipitation': weather.precipitation,
            'windSpeed': weather.windSpeed,
            'position_lat': weather.position_lat,
            'position_lon': weather.position_lon
        }
    except DoesNotExist:
        return None


def get_all_weather(limit=100, offset=0):
    """Get all weather records with pagination, ordered by date descending"""
    weather_records = Weather.select().order_by(Weather.date.desc()).limit(limit).offset(offset)
    return [
        {
            'id': w.id,
            'date': w.date,
            'temperature': w.temperature,
            'precipitation': w.precipitation,
            'windSpeed': w.windSpeed,
            'position_lat': w.position_lat,
            'position_lon': w.position_lon
        }
        for w in weather_records
    ]


def get_weather_by_location(lat, lon, limit=10):
    """Get weather records for a specific location
    
    Note: Uses exact coordinate matching. For real-world applications,
    consider implementing a bounding box or distance-based query.
    """
    weather_records = Weather.select().where(
        (Weather.position_lat == lat) & (Weather.position_lon == lon)
    ).limit(limit)
    return [
        {
            'id': w.id,
            'date': w.date,
            'temperature': w.temperature,
            'precipitation': w.precipitation,
            'windSpeed': w.windSpeed,
            'position_lat': w.position_lat,
            'position_lon': w.position_lon
        }
        for w in weather_records
    ]


def get_weather_by_date_range(start_date, end_date, limit=100):
    """Get weather records within a date range"""
    weather_records = Weather.select().where(
        (Weather.date >= start_date) & (Weather.date <= end_date)
    ).limit(limit)
    return [
        {
            'id': w.id,
            'date': w.date,
            'temperature': w.temperature,
            'precipitation': w.precipitation,
            'windSpeed': w.windSpeed,
            'position_lat': w.position_lat,
            'position_lon': w.position_lon
        }
        for w in weather_records
    ]


def count_weather_records():
    """Count total number of weather records"""
    return Weather.select().count()


# ==================== UPDATE OPERATIONS ====================

def update_weather(weather_id, date=None, temperature=None, precipitation=None, wind_speed=None, position_lat=None, position_lon=None):
    """Update a weather record"""
    try:
        weather = Weather.get_by_id(weather_id)
        
        # Update only provided fields
        if date is not None:
            weather.date = date
        if temperature is not None:
            weather.temperature = temperature
        if precipitation is not None:
            weather.precipitation = precipitation
        if wind_speed is not None:
            weather.windSpeed = wind_speed
        if position_lat is not None:
            weather.position_lat = position_lat
        if position_lon is not None:
            weather.position_lon = position_lon
        
        weather.save()
        return True
    except DoesNotExist:
        return False


# ==================== DELETE OPERATIONS ====================

def delete_weather(weather_id):
    """Delete a weather record by ID"""
    try:
        weather = Weather.get_by_id(weather_id)
        weather.delete_instance()
        return True
    except DoesNotExist:
        return False


def delete_weather_by_date(date):
    """Delete weather records by date"""
    count = Weather.delete().where(Weather.date == date).execute()
    return count


def delete_all_weather():
    """Delete all weather records"""
    count = Weather.delete().execute()
    return count
