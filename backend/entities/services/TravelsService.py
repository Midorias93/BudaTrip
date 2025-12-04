from backend.entities.models.TravelsModel import Travel, TransportType
from peewee import DoesNotExist


# ==================== CREATE OPERATIONS ====================

def create_travel(user_id, duration=None, distance=None, start_lat=None, start_lon=None, 
                 end_lat=None, end_lon=None, transport_type=None, cost=None, 
                 co2_emissions=None, weather_id=None, pass_id=None):
    """Create a new travel record"""
    try:
        travel = Travel.create(
            user_id=user_id,
            duration=duration,
            distance=distance,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            transportType=transport_type,
            cost=cost,
            CO2Emissions=co2_emissions,
            weather_id=weather_id,
            pass_id=pass_id
        )
        return travel.id
    except Exception as e:
        print(f"Error creating travel: {e}")
        return None


# ==================== READ OPERATIONS ====================

def get_travel_by_id(travel_id):
    """Get a travel record by ID"""
    try:
        travel = Travel.get_by_id(travel_id)
        return {
            'id': travel.id,
            'user_id': travel.user_id.id,
            'duration': travel.duration,
            'distance': travel.distance,
            'start_lat': travel.start_lat,
            'start_lon': travel.start_lon,
            'end_lat': travel.end_lat,
            'end_lon': travel.end_lon,
            'transportType': travel.transportType,
            'cost': travel.cost,
            'CO2Emissions': travel.CO2Emissions,
            'weather_id': travel.weather_id.id if travel.weather_id else None,
            'pass_id': travel.pass_id.id if travel.pass_id else None
        }
    except DoesNotExist:
        return None


def get_all_travels(limit=100, offset=0):
    """Get all travel records with pagination"""
    travels = Travel.select().limit(limit).offset(offset)
    return [
        {
            'id': t.id,
            'user_id': t.user_id.id,
            'duration': t.duration,
            'distance': t.distance,
            'start_lat': t.start_lat,
            'start_lon': t.start_lon,
            'end_lat': t.end_lat,
            'end_lon': t.end_lon,
            'transportType': t.transportType,
            'cost': t.cost,
            'CO2Emissions': t.CO2Emissions,
            'weather_id': t.weather_id.id if t.weather_id else None,
            'pass_id': t.pass_id.id if t.pass_id else None
        }
        for t in travels
    ]


def get_travels_by_user(user_id, limit=100, offset=0):
    """Get all travels for a specific user"""
    travels = Travel.select().where(Travel.user_id == user_id).limit(limit).offset(offset)
    return [
        {
            'id': t.id,
            'user_id': t.user_id.id,
            'duration': t.duration,
            'distance': t.distance,
            'start_lat': t.start_lat,
            'start_lon': t.start_lon,
            'end_lat': t.end_lat,
            'end_lon': t.end_lon,
            'transportType': t.transportType,
            'cost': t.cost,
            'CO2Emissions': t.CO2Emissions,
            'weather_id': t.weather_id.id if t.weather_id else None,
            'pass_id': t.pass_id.id if t.pass_id else None
        }
        for t in travels
    ]


def get_travels_by_transport_type(transport_type, limit=100):
    """Get all travels by transport type"""
    travels = Travel.select().where(Travel.transportType == transport_type).limit(limit)
    return [
        {
            'id': t.id,
            'user_id': t.user_id.id,
            'duration': t.duration,
            'distance': t.distance,
            'start_lat': t.start_lat,
            'start_lon': t.start_lon,
            'end_lat': t.end_lat,
            'end_lon': t.end_lon,
            'transportType': t.transportType,
            'cost': t.cost,
            'CO2Emissions': t.CO2Emissions,
            'weather_id': t.weather_id.id if t.weather_id else None,
            'pass_id': t.pass_id.id if t.pass_id else None
        }
        for t in travels
    ]


def count_travels():
    """Count total number of travels"""
    return Travel.select().count()


def count_travels_by_user(user_id):
    """Count travels for a specific user"""
    return Travel.select().where(Travel.user_id == user_id).count()


def get_total_distance_by_user(user_id):
    """Get total distance traveled by a user"""
    from peewee import fn
    result = Travel.select(fn.SUM(Travel.distance)).where(Travel.user_id == user_id).scalar()
    return result if result else 0


def get_total_co2_by_user(user_id):
    """Get total CO2 emissions by a user"""
    from peewee import fn
    result = Travel.select(fn.SUM(Travel.CO2Emissions)).where(Travel.user_id == user_id).scalar()
    return result if result else 0


# ==================== UPDATE OPERATIONS ====================

def update_travel(travel_id, duration=None, distance=None, start_lat=None, start_lon=None,
                 end_lat=None, end_lon=None, transport_type=None, cost=None,
                 co2_emissions=None, weather_id=None, pass_id=None):
    """Update a travel record"""
    try:
        travel = Travel.get_by_id(travel_id)
        
        # Update only provided fields
        if duration is not None:
            travel.duration = duration
        if distance is not None:
            travel.distance = distance
        if start_lat is not None:
            travel.start_lat = start_lat
        if start_lon is not None:
            travel.start_lon = start_lon
        if end_lat is not None:
            travel.end_lat = end_lat
        if end_lon is not None:
            travel.end_lon = end_lon
        if transport_type is not None:
            travel.transportType = transport_type
        if cost is not None:
            travel.cost = cost
        if co2_emissions is not None:
            travel.CO2Emissions = co2_emissions
        if weather_id is not None:
            travel.weather_id = weather_id
        if pass_id is not None:
            travel.pass_id = pass_id
        
        travel.save()
        return True
    except DoesNotExist:
        return False


# ==================== DELETE OPERATIONS ====================

def delete_travel(travel_id):
    """Delete a travel record by ID"""
    try:
        travel = Travel.get_by_id(travel_id)
        travel.delete_instance()
        return True
    except DoesNotExist:
        return False


def delete_travels_by_user(user_id):
    """Delete all travels for a user"""
    count = Travel.delete().where(Travel.user_id == user_id).execute()
    return count


def delete_all_travels():
    """Delete all travel records"""
    count = Travel.delete().execute()
    return count
