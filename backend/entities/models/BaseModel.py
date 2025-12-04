from peewee import Model
from backend.config import db

class BaseModel(Model):
    """Base model class that all models will inherit from"""
    class Meta:
        database = db

