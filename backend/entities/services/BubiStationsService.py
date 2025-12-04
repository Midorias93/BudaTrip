from backend.entities.models.BubiStationsModel import BubiStation
from peewee import DoesNotExist


# ==================== CREATE OPERATIONS ====================

def create_bubi_station():
    """Create a new Bubi station"""
    try:
        station = BubiStation.create()
        return station.id
    except Exception as e:
        print(f"Error creating Bubi station: {e}")
        return None


# ==================== READ OPERATIONS ====================

def get_bubi_station_by_id(station_id):
    """Get a Bubi station by ID"""
    try:
        station = BubiStation.get_by_id(station_id)
        return {
            'id': station.id,
        }
    except DoesNotExist:
        return None


def get_all_bubi_stations(limit=100, offset=0):
    """Get all Bubi stations with pagination"""
    stations = BubiStation.select().limit(limit).offset(offset)
    return [
        {
            'id': station.id,
        }
        for station in stations
    ]


def count_bubi_stations():
    """Count total number of Bubi stations"""
    return BubiStation.select().count()


def bubi_station_exists(station_id):
    """Check if a Bubi station exists"""
    return BubiStation.select().where(BubiStation.id == station_id).exists()


# ==================== UPDATE OPERATIONS ====================

def update_bubi_station(station_id):
    """Update a Bubi station's information"""
    try:
        station = BubiStation.get_by_id(station_id)
        station.save()
        return True
    except DoesNotExist:
        return False


# ==================== DELETE OPERATIONS ====================

def delete_bubi_station(station_id):
    """Delete a Bubi station by ID"""
    try:
        station = BubiStation.get_by_id(station_id)
        station.delete_instance()
        return True
    except DoesNotExist:
        return False


def delete_all_bubi_stations():
    """Delete all Bubi stations"""
    count = BubiStation.delete().execute()
    return count
