from backend.entities.models.BKKStationsModel import BKKStation
from backend.statics.localisation.toolsLocalisation import haversine_distance


def find_nearest_bkk_stop(lat, lon):
    """
    Returns the nearest BKK stop from the GTFS stops table.
    Expects a GTFS-like schema with columns: stop_id, stop_name, stop_lat, stop_lon.
    
    Args:
        lat: Latitude of the user location
        lon: Longitude of the user location
    
    Returns:
        Dictionary with stop information or None if no stops found
    """
    stops = BKKStation.select().where(
        (BKKStation.stop_lat.is_null(False)) & 
        (BKKStation.stop_lon.is_null(False))
    )

    nearest_stop = None
    min_distance = float('inf')
    user_coords = (lat, lon)
    
    for stop in stops:
        stop_coords = (stop.stop_lat, stop.stop_lon)
        distance = haversine_distance(user_coords, stop_coords)
        if distance < min_distance:
            min_distance = distance
            nearest_stop = {
                'stop_id': stop.stop_id,
                'stop_name': stop.stop_name,
                'stop_lat': stop.stop_lat,
                'stop_lon': stop.stop_lon
            }

    return nearest_stop
