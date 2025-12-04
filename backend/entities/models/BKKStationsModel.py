from peewee import CharField, DoubleField, IntegerField
from entities.models.BaseModel import BaseModel

class BKKStation(BaseModel):
    """BKK Station model representing the bkk table"""
    stop_id = CharField(max_length=20, primary_key=True)
    stop_code = CharField(max_length=20, null=True)
    stop_name = CharField(max_length=100, null=True)
    stop_lat = DoubleField(null=True)
    stop_lon = DoubleField(null=True)
    zone_id = CharField(max_length=20, null=True)
    stop_url = CharField(max_length=200, null=True)
    location_type = IntegerField(null=True)
    parent_station = CharField(max_length=100, null=True)
    stop_desc = CharField(max_length=200, null=True)
    stop_timezone = CharField(max_length=50, null=True)
    wheelchair_boarding = IntegerField(null=True)
    level_id = CharField(max_length=20, null=True)
    platform_code = CharField(max_length=20, null=True)
    location_sub_type = CharField(max_length=100, null=True)

    class Meta:
        table_name = 'bkk'
