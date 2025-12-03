from peewee import (
    Model, 
    PostgresqlDatabase, 
    CharField, 
    IntegerField, 
    AutoField,
    DoubleField
)
from config import Config

# Initialize database connection
db = PostgresqlDatabase(
    Config.POSTGRES_DB,
    user=Config.POSTGRES_USER,
    password=Config.POSTGRES_PASSWORD,
    host=Config.POSTGRES_HOST,
    port=int(Config.POSTGRES_PORT)
)


class BaseModel(Model):
    """Base model class that all models will inherit from"""
    class Meta:
        database = db


class User(BaseModel):
    """User model representing the users table"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, null=True)
    email = CharField(max_length=100, unique=True)
    phone = CharField(max_length=12, unique=True, null=True)
    password = CharField(max_length=100)

    class Meta:
        table_name = 'users'


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


def initialize_database():
    """Connect to the database and create tables if they don't exist"""
    db.connect(reuse_if_open=True)
    db.create_tables([User, BKKStation], safe=True)
    print("Database initialized and tables created")


def close_database():
    """Close the database connection"""
    if not db.is_closed():
        db.close()
        print("Database connection closed")
