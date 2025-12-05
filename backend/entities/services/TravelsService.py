from backend.entities.models.TravelsModel import Travel
from backend.entities.models.PassesModel import Pass
from peewee import DoesNotExist, fn


# ==================== ESTIMATION CONSTANTS ====================

# CO2 emission constants (grams per kilometer)
CO2_EMISSIONS = {
    'CAR': 170,           # Car produces 170g of CO2 per km
    'TRANSPORT': 3,       # Public transport produces 3g per km
    'BUBI': 0,            # Bubi bike-sharing produces 0g of CO2
    'BIKE': 0,            # Personal bike produces 0g of CO2
    'WALK': 0             # Walking produces 0g of CO2
}

# Cost constants (Forint)
COST_PER_TRAVEL = 250      # 250 Forint per travel for public transport and Bubi (without pass)
COST_PER_KM_CAR = 50  # 0.70 Forint per kilometer for car


def calculate_travel_cost(user_id, transport_type, distance):
    """
    Calculate the cost for a travel based on transport type and user passes.
    
    Args:
        user_id: The ID of the user
        transport_type: The type of transport
        distance: Distance in meters
    
    Returns:
        Cost in Forint
    """
    if not transport_type or not distance:
        return 0
    
    try:
        transport_upper = transport_type.upper()
        
        # Check what passes the user has
        user_passes = list(Pass.select().where(Pass.user_id == user_id))
        pass_types = [p.type for p in user_passes]
        has_bkk_pass = 'BKK' in pass_types
        has_bubi_pass = 'BUBI' in pass_types
        
        cost = 0
        
        if transport_upper == 'CAR':
            # Car: 0.70 Forint per kilometer
            distance_km = distance
            cost = distance_km * COST_PER_KM_CAR
        elif transport_upper == 'TRANSPORT':
            # Public transport: Free with BKK pass, otherwise 250 per travel
            if not has_bkk_pass:
                cost = COST_PER_TRAVEL
        elif transport_upper == 'BUBI':
            # Bubi bike-sharing: Free with BUBI pass, otherwise 250 per travel
            if not has_bubi_pass:
                cost = COST_PER_TRAVEL
        elif transport_upper in ['BIKE', 'WALK']:
            # Personal bike and walking are always free
            cost = 0
        
        return cost
    except Exception as e:
        print(f"Error calculating travel cost: {e}")
        return 0


def calculate_travel_co2(transport_type, distance):
    """
    Calculate the CO2 emissions for a travel based on transport type and distance.
    
    Args:
        transport_type: The type of transport
        distance: Distance in meters
    
    Returns:
        CO2 emissions in grams
    """
    if not transport_type or not distance:
        return 0
    
    try:
        transport_upper = transport_type.upper()
        distance_km = distance
        emission_rate = CO2_EMISSIONS.get(transport_upper, 0)
        co2_grams = distance_km * emission_rate
        return co2_grams
    except Exception as e:
        print(f"Error calculating CO2 emissions: {e}")
        return 0


# ==================== CREATE OPERATIONS ====================

def create_travel(user_id, duration=None, distance=None, start_lat=None, start_lon=None, 
                 end_lat=None, end_lon=None, transport_type=None, cost=None, 
                 co2_emissions=None, weather_id=None):
    """Create a new travel record
    
    Args:
        user_id: Required. ID of the user who made the travel.
        Other parameters are optional travel attributes.
        If cost or co2_emissions are not provided, they will be calculated automatically.
    
    Returns:
        Travel ID if successful, None otherwise.
    """
    if user_id is None:
        print("Error: user_id is required")
        return None
    
    # Calculate cost if not provided
    if cost == 0 and transport_type and distance:
        cost = calculate_travel_cost(user_id, transport_type, distance)
    # Calculate CO2 emissions if not provided
    if co2_emissions is None and transport_type and distance:
        co2_emissions = calculate_travel_co2(transport_type, distance)
        
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
            'user_id': travel.user_id.id if travel.user_id else None,
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
        }
    except DoesNotExist:
        return None


def get_all_travels(limit=100, offset=0):
    """Get all travel records with pagination"""
    travels = Travel.select().limit(limit).offset(offset)
    return [
        {
            'id': t.id,
            'user_id': t.user_id.id if t.user_id else None,
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
        }
        for t in travels
    ]


def get_travels_by_user(user_id, limit=100, offset=0):
    """Get all travels for a specific user"""
    travels = Travel.select().where(Travel.user_id == user_id).limit(limit).offset(offset)
    return [
        {
            'id': t.id,
            'user_id': t.user_id.id if t.user_id else None,
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
        }
        for t in travels
    ]


def get_travels_by_transport_type(transport_type, limit=100):
    """Get all travels by transport type"""
    travels = Travel.select().where(Travel.transportType == transport_type).limit(limit)
    return [
        {
            'id': t.id,
            'user_id': t.user_id.id if t.user_id else None,
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
    result = Travel.select(fn.SUM(Travel.distance)).where(Travel.user_id == user_id).scalar()
    return result if result else 0


def get_total_co2_by_user(user_id):
    """Get total CO2 emissions by a user"""
    result = Travel.select(fn.SUM(Travel.CO2Emissions)).where(Travel.user_id == user_id).scalar()
    return result if result else 0


def get_total_cost_by_user(user_id):
    """Get total cost by a user"""
    result = Travel.select(fn.SUM(Travel.cost)).where(Travel.user_id == user_id).scalar()
    return result if result else 0


def get_distance_by_transport(user_id):
    """
    Get distance traveled by transport type for a user.
    
    Returns:
        Dictionary with transport types as keys and distances (in meters) as values
    """
    try:
        distances = (Travel
                    .select(Travel.transportType, fn.SUM(Travel.distance).alias('total_distance'))
                    .where(Travel.user_id == user_id)
                    .group_by(Travel.transportType))
        
        result = {}
        for travel in distances:
            if travel.transportType and travel.total_distance:
                result[travel.transportType] = float(travel.total_distance)
        
        return result
    except Exception as e:
        print(f"Error getting distance by transport for user {user_id}: {e}")
        return {}


def get_co2_by_transport(user_id):
    """
    Get CO2 emissions by transport type for a user.
    
    Returns:
        Dictionary with transport types as keys and CO2 emissions (in grams) as values
    """
    try:
        co2_data = (Travel
                   .select(Travel.transportType, fn.SUM(Travel.CO2Emissions).alias('total_co2'))
                   .where(Travel.user_id == user_id)
                   .group_by(Travel.transportType))
        
        result = {}
        for travel in co2_data:
            if travel.transportType and travel.total_co2:
                result[travel.transportType] = float(travel.total_co2)
        
        return result
    except Exception as e:
        print(f"Error getting CO2 by transport for user {user_id}: {e}")
        return {}


def get_cost_by_transport(user_id):
    """
    Get cost by transport type for a user.
    
    Returns:
        Dictionary with transport types as keys and costs (in Forint) as values
    """
    try:
        cost_data = (Travel
                    .select(Travel.transportType, fn.SUM(Travel.cost).alias('total_cost'))
                    .where(Travel.user_id == user_id)
                    .group_by(Travel.transportType))
        
        result = {}
        for travel in cost_data:
            if travel.transportType and travel.total_cost:
                result[travel.transportType] = float(travel.total_cost)
        
        return result
    except Exception as e:
        print(f"Error getting cost by transport for user {user_id}: {e}")
        return {}


# ==================== UPDATE OPERATIONS ====================

def update_travel(travel_id, duration=None, distance=None, start_lat=None, start_lon=None,
                 end_lat=None, end_lon=None, transport_type=None, cost=None,
                 co2_emissions=None, weather_id=None):
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
