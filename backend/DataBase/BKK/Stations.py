from entities.models.BKKStationsModel import BKKStation
from peewee import DoesNotExist
import csv


def fill_bkk_table():
    """Fills the bkk table with data from the stops.txt file"""
    try:
        # Empty the table before filling it
        BKKStation.delete().execute()

        # Read the file with the csv module which handles quotes
        with open('DataBase/BKK/stops.txt', 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)

            stations_to_insert = []
            for row in csv_reader:
                station_data = {
                    'stop_id': row['stop_id'],
                    'stop_code': row['stop_code'] or None,
                    'stop_name': row['stop_name'],
                    'stop_lat': float(row['stop_lat']) if row['stop_lat'] else None,
                    'stop_lon': float(row['stop_lon']) if row['stop_lon'] else None,
                    'zone_id': row['zone_id'] or None,
                    'stop_url': row['stop_url'] or None,
                    'location_type': int(row['location_type']) if row['location_type'] else 0,
                    'parent_station': row['parent_station'] or None,
                    'stop_desc': row['stop_desc'] or None,
                    'stop_timezone': row['stop_timezone'] or None,
                    'wheelchair_boarding': int(row['wheelchair_boarding']) if row['wheelchair_boarding'] else None,
                    'level_id': row['level_id'] or None,
                    'platform_code': row['platform_code'] or None
                }
                stations_to_insert.append(station_data)

            # Batch insert for better performance
            if stations_to_insert:
                # Insert in batches of 100
                for i in range(0, len(stations_to_insert), 100):
                    batch = stations_to_insert[i:i + 100]
                    BKKStation.insert_many(batch).execute()

        print(f"Table bkk filled successfully with {len(stations_to_insert)} stations")

    except Exception as e:
        print(f"Error during filling: {e}")
        raise


def get_all_bkk_stations():
    """Get all BKK stations"""
    stations = BKKStation.select()
    return [
        {
            'stop_id': station.stop_id,
            'stop_code': station.stop_code,
            'stop_name': station.stop_name,
            'stop_lat': station.stop_lat,
            'stop_lon': station.stop_lon,
            'zone_id': station.zone_id,
            'stop_url': station.stop_url,
            'location_type': station.location_type,
            'parent_station': station.parent_station,
            'stop_desc': station.stop_desc,
            'stop_timezone': station.stop_timezone,
            'wheelchair_boarding': station.wheelchair_boarding,
            'level_id': station.level_id,
            'platform_code': station.platform_code,
            'location_sub_type': station.location_sub_type
        }
        for station in stations
    ]


def get_bkk_station_by_stop_id(stop_id):
    """Get a BKK station by stop_id"""
    try:
        station = BKKStation.get(BKKStation.stop_id == stop_id)
        return {
            'stop_id': station.stop_id,
            'stop_code': station.stop_code,
            'stop_name': station.stop_name,
            'stop_lat': station.stop_lat,
            'stop_lon': station.stop_lon,
            'zone_id': station.zone_id,
            'stop_url': station.stop_url,
            'location_type': station.location_type,
            'parent_station': station.parent_station,
            'stop_desc': station.stop_desc,
            'stop_timezone': station.stop_timezone,
            'wheelchair_boarding': station.wheelchair_boarding,
            'level_id': station.level_id,
            'platform_code': station.platform_code,
            'location_sub_type': station.location_sub_type
        }
    except DoesNotExist:
        return None


def get_bkk_station_by_name(name):
    """Get a BKK station by name"""
    try:
        station = BKKStation.get(BKKStation.stop_name == name)
        return {
            'stop_id': station.stop_id,
            'stop_code': station.stop_code,
            'stop_name': station.stop_name,
            'stop_lat': station.stop_lat,
            'stop_lon': station.stop_lon,
            'zone_id': station.zone_id,
            'stop_url': station.stop_url,
            'location_type': station.location_type,
            'parent_station': station.parent_station,
            'stop_desc': station.stop_desc,
            'stop_timezone': station.stop_timezone,
            'wheelchair_boarding': station.wheelchair_boarding,
            'level_id': station.level_id,
            'platform_code': station.platform_code,
            'location_sub_type': station.location_sub_type
        }
    except DoesNotExist:
        return None


def clear_bkk_table():
    """Clear all data from the bkk table"""
    BKKStation.delete().execute()
