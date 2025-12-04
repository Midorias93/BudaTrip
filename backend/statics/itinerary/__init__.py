# Itinerary package initialization
from . import BikeItinerary
from . import CarItinerary
from . import TransportItinerary
# Import with the special name
import importlib
TransportBikeItinerary = importlib.import_module('.Transport&BikeItinerary', package='backend.statics.itinerary')

# For backward compatibility, expose the old Itinerary module
class Itinerary:
    """Backward compatibility wrapper for Itinerary module"""
    # Use BikeItinerary's get_route as default since the original supported bike/foot modes
    get_route = staticmethod(BikeItinerary.get_route)
