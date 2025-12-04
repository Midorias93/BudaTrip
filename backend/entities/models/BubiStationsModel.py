from peewee import AutoField
from backend.entities.models.BaseModel import BaseModel

class BubiStation(BaseModel):
    """Bubi Station model representing the bubi_stations table"""
    id = AutoField(primary_key=True)

    class Meta:
        table_name = 'bubi_stations'
        schema = 'public'
