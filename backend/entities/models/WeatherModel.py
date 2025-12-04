from peewee import AutoField, DateTimeField, IntegerField, DoubleField
from backend.entities.models.BaseModel import BaseModel

class Weather(BaseModel):
    """Weather model representing the weather table"""
    id = AutoField(primary_key=True)
    date = DateTimeField(null=False)
    temperature = IntegerField(null=True)
    precipitation = IntegerField(null=True)
    windSpeed = IntegerField(null=True)
    position_lat = DoubleField(null=False)
    position_lon = DoubleField(null=False)

    class Meta:
        table_name = 'weather'
        schema = 'public'
