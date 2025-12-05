"""
Account statistics module for calculating user travel statistics.

This module provides functions to compute:
- Distance traveled by transport type
- CO2 emissions based on transport type
- Travel costs based on pass ownership and transport type
"""

import logging
from peewee import fn
from backend.entities.models.TravelsModel import Travel, TransportType
from backend.entities.models.PassesModel import Pass
from backend.entities.models.UserModel import User

logger = logging.getLogger(__name__)


# CO2 emission constants (grams per kilometer)
CO2_EMISSIONS = {
    'CAR': 180,           # Car produces 180g of CO2 per km
    'BUS': 2,             # Public transport produces 2g per km
    'TRAIN': 2,           # Public transport produces 2g per km
    'TRAM': 2,            # Public transport produces 2g per km
    'SUBWAY': 2,          # Public transport produces 2g per km
    'BIKE': 0,            # Bike produces 0g of CO2
    'WALK': 0             # Walking produces 0g of CO2
}

# Cost constants (Forint)
COST_PER_TRAVEL = 250      # 250 Forint per travel for public transport and Bubi (without pass)
COST_PER_KM_CAR = 250      # 250 Forint per kilometer for car


def get_user_distance_by_transport(user_id):
    """
    Calculate the total distance traveled by a user for each transport type.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        Dictionary with transport types as keys and distances (in meters) as values
        Example: {
            'CAR': 15000.5,
            'BUS': 8000.0,
            'BIKE': 5000.0,
            'WALK': 2000.0
        }
    """
    try:
        # Query to aggregate distance by transport type for the user
        distances = (Travel
                    .select(Travel.transportType, fn.SUM(Travel.distance).alias('total_distance'))
                    .where(Travel.user_id == user_id)
                    .group_by(Travel.transportType))
        
        # Build result dictionary
        result = {}
        for travel in distances:
            if travel.transportType and travel.total_distance:
                result[travel.transportType] = float(travel.total_distance)
        
        return result
    
    except Exception as e:
        logger.error(f"Error calculating distance by transport for user {user_id}: {e}")
        return {}


def get_user_pollution(user_id):
    """
    Calculate the total CO2 emissions produced by a user's travels.
    
    CO2 emission rates:
    - Car: 180 grams per kilometer
    - Public transport (BUS, TRAIN, TRAM, SUBWAY): 2 grams per kilometer
    - Bike and Walk: 0 grams per kilometer
    
    Args:
        user_id: The ID of the user
    
    Returns:
        Dictionary with:
        - 'total_co2': Total CO2 emissions in grams
        - 'by_transport': CO2 emissions by transport type
        Example: {
            'total_co2': 5400.0,
            'by_transport': {
                'CAR': 5400.0,
                'BUS': 16.0,
                'BIKE': 0.0
            }
        }
    """
    try:
        distances = get_user_distance_by_transport(user_id)
        
        co2_by_transport = {}
        total_co2 = 0.0
        
        for transport_type, distance_meters in distances.items():
            # Convert distance from meters to kilometers
            distance_km = distance_meters / 1000.0
            
            # Get CO2 emission rate for this transport type
            emission_rate = CO2_EMISSIONS.get(transport_type.upper(), 0)
            
            # Calculate CO2 for this transport type
            co2_grams = distance_km * emission_rate
            co2_by_transport[transport_type] = co2_grams
            total_co2 += co2_grams
        
        return {
            'total_co2': total_co2,
            'by_transport': co2_by_transport
        }
    
    except Exception as e:
        logger.error(f"Error calculating pollution for user {user_id}: {e}")
        return {
            'total_co2': 0.0,
            'by_transport': {}
        }


def _user_has_pass(user_id, pass_type=None):
    """
    Check if a user has a specific pass or any pass.
    
    Args:
        user_id: The ID of the user
        pass_type: Optional - specific pass type to check (BKK, BUBI, etc.)
    
    Returns:
        Boolean indicating if user has the pass
    """
    try:
        query = Pass.select().where(Pass.user_id == user_id)
        
        if pass_type:
            query = query.where(Pass.type == pass_type)
        
        return query.exists()
    
    except Exception as e:
        logger.error(f"Error checking pass for user {user_id}: {e}")
        return False


def get_user_cost(user_id):
    """
    Calculate the total cost of all travels for a user.
    
    Cost rules:
    - If user has BKK pass: Public transport (BUS, TRAIN, TRAM, SUBWAY) is free
    - If user has BUBI pass: Bubi bikes are free
    - Without pass: 250 Forint per travel for public transport and Bubi
    - Bike (personal): Always free
    - Walk: Always free
    - Car: 250 Forint per kilometer
    
    Note: The current implementation cannot distinguish between personal bikes and Bubi.
    All BIKE transport is treated as potentially Bubi and charged unless user has BUBI pass.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        Dictionary with:
        - 'total_cost': Total cost in Forint
        - 'by_transport': Cost breakdown by transport type
        - 'passes': List of pass types the user has
        Example: {
            'total_cost': 12500.0,
            'by_transport': {
                'CAR': 7500.0,
                'BUS': 5000.0,
                'BIKE': 0.0
            },
            'passes': ['BKK', 'BUBI']
        }
    """
    try:
        # Check what passes the user has
        user_passes = list(Pass.select().where(Pass.user_id == user_id))
        pass_types = [p.type for p in user_passes]
        has_bkk_pass = 'BKK' in pass_types
        has_bubi_pass = 'BUBI' in pass_types
        
        # Get all travels for the user
        travels = Travel.select().where(Travel.user_id == user_id)
        
        cost_by_transport = {}
        total_cost = 0.0
        
        for travel in travels:
            transport_type = travel.transportType
            if not transport_type:
                continue
            
            transport_upper = transport_type.upper()
            cost = 0.0
            
            # Calculate cost based on transport type and passes
            if transport_upper == 'CAR':
                # Car: 250 Forint per kilometer
                if travel.distance:
                    distance_km = travel.distance / 1000.0
                    cost = distance_km * COST_PER_KM_CAR
            
            elif transport_upper in ['BUS', 'TRAIN', 'TRAM', 'SUBWAY']:
                # Public transport: Free with BKK pass, otherwise 250 per travel
                if not has_bkk_pass:
                    cost = COST_PER_TRAVEL
            
            elif transport_upper == 'BIKE':
                # Need to determine if it's Bubi or personal bike
                # For Bubi: Free with BUBI pass, otherwise 250 per travel
                # For personal bike: Always free
                # Since we can't distinguish in current model, we'll check for Bubi pass
                if not has_bubi_pass:
                    cost = COST_PER_TRAVEL
                # Note: Personal bikes would be free, but we treat all BIKE as potentially Bubi
            
            elif transport_upper == 'WALK':
                # Walking is always free
                cost = 0.0
            
            # Add to totals
            if transport_type not in cost_by_transport:
                cost_by_transport[transport_type] = 0.0
            cost_by_transport[transport_type] += cost
            total_cost += cost
        
        return {
            'total_cost': total_cost,
            'by_transport': cost_by_transport,
            'passes': pass_types
        }
    
    except Exception as e:
        logger.error(f"Error calculating cost for user {user_id}: {e}")
        return {
            'total_cost': 0.0,
            'by_transport': {},
            'passes': []
        }


def get_user_statistics(user_id):
    """
    Get comprehensive statistics for a user including distances, pollution, and costs.
    
    This is the main function that aggregates all statistics for a user.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        Dictionary with complete user statistics:
        {
            'user_id': int,
            'distances': {
                'total': float (meters),
                'by_transport': {transport_type: distance_meters}
            },
            'pollution': {
                'total_co2': float (grams),
                'by_transport': {transport_type: co2_grams}
            },
            'costs': {
                'total_cost': float (Forint),
                'by_transport': {transport_type: cost_forint},
                'passes': [pass_types]
            }
        }
    """
    try:
        # Verify user exists
        user_exists = User.select().where(User.id == user_id).exists()
        if not user_exists:
            logger.warning(f"User with ID {user_id} does not exist")
            return None
        
        # Get distance statistics
        distances_by_transport = get_user_distance_by_transport(user_id)
        total_distance = sum(distances_by_transport.values())
        
        # Get pollution statistics
        pollution = get_user_pollution(user_id)
        
        # Get cost statistics
        costs = get_user_cost(user_id)
        
        return {
            'user_id': user_id,
            'distances': {
                'total': total_distance,
                'by_transport': distances_by_transport
            },
            'pollution': pollution,
            'costs': costs
        }
    
    except Exception as e:
        logger.error(f"Error getting statistics for user {user_id}: {e}")
        return None
