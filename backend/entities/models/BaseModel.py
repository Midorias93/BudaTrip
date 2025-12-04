from peewee import Model
from config import db

class BaseModel(Model):
    """Base model class that all models will inherit from"""
    class Meta:
        database = db

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
