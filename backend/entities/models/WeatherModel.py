from peewee import AutoField, DateTimeField, IntegerField, CharField
from backend.entities.models.BaseModel import BaseModel

class Weather(BaseModel):
    """Weather model representing the weather table"""
    id = AutoField(primary_key=True)
    date = DateTimeField(null=False)
    temperature = IntegerField(null=True)
    precipitation = IntegerField(null=True)
    windSpeed = IntegerField(null=True)
    # Storing position as "lat,lon" string format, as Peewee doesn't have Pair type
    # Alternative: use separate latitude/longitude fields
    position = CharField(max_length=50, null=False)  # Format: "lat,lon"

    class Meta:
        table_name = 'weather'
        schema = 'public'
