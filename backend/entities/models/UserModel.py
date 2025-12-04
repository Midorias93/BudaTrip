from peewee import (
    Model,
    PostgresqlDatabase,
    CharField,
    IntegerField,
    AutoField,
    DoubleField
)
from backend.entities.models.BaseModel import BaseModel

class User(BaseModel):
    """User model representing the users table"""
    id = AutoField(primary_key=True)
    name = CharField(max_length=100, null=True)
    email = CharField(max_length=100, unique=True)
    phone = CharField(max_length=12, unique=True, null=True)
    password = CharField(max_length=100)

    class Meta:
        table_name = 'users'
