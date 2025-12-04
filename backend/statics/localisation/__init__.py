# Localisation package initialization
from . import UserLocalisation
from . import BubiLocalisation
from . import BKKLocalisation
from . import toolsLocalisation

# For backward compatibility, expose the old module names
# This allows existing code to continue using: from backend.statics.localisation import Location
class Location:
    """Backward compatibility wrapper for Location module"""
    # User location functions
    get_location = staticmethod(UserLocalisation.get_location)
    get_my_coordinates = staticmethod(UserLocalisation.get_my_coordinates)
    
    # Bubi station functions
    bubi_location = staticmethod(BubiLocalisation.bubi_location)
    find_nearest_station = staticmethod(BubiLocalisation.find_nearest_station)
    
    # BKK station functions
    find_nearest_bkk_stop = staticmethod(BKKLocalisation.find_nearest_bkk_stop)
    
    # Tool functions
    haversine_distance = staticmethod(toolsLocalisation.haversine_distance)
    get_coordinates = staticmethod(toolsLocalisation.get_coordinates)
