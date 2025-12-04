from enum import Enum
from peewee import (
    AutoField,
    DateTimeField,
    DoubleField,
    CharField,
    BigIntegerField,
    ForeignKeyField,
    DeferredForeignKey
)
from backend.entities.models.BaseModel import BaseModel
from backend.entities.models.UserModel import User
from backend.entities.models.WeatherModel import Weather


class TransportType(Enum):
    """Enum for transport types"""
    BUS = "BUS"
    TRAIN = "TRAIN"
    TRAM = "TRAM"
    BIKE = "BIKE"
    WALK = "WALK"
    CAR = "CAR"
    SUBWAY = "SUBWAY"


class Travel(BaseModel):
    """Travel model representing the travel table"""
    id = AutoField(primary_key=True)
    user_id = ForeignKeyField(User, backref='travels', null=False, on_delete='CASCADE')
    duration = DateTimeField(null=True)  # Using DateTimeField for Instant
    distance = DoubleField(null=True)
    # Storing positions as "lat,lon" string format
    startPosition = CharField(max_length=50, null=True)  # Format: "lat,lon"
    endPosition = CharField(max_length=50, null=True)  # Format: "lat,lon"
    transportType = CharField(max_length=20, null=True)  # Storing enum as string
    cost = BigIntegerField(null=True)
    CO2Emissions = BigIntegerField(null=True)
    weather_id = ForeignKeyField(Weather, backref='travels', null=True, on_delete='SET NULL')
    # Using DeferredForeignKey to avoid circular import with PassesModel
    pass_id = DeferredForeignKey('Pass', backref='travels', null=True, on_delete='SET NULL')

    class Meta:
        table_name = 'travel'
        schema = 'public'
