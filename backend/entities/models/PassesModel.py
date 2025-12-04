from enum import Enum
from peewee import AutoField, CharField, DoubleField, ForeignKeyField
from backend.entities.models.BaseModel import BaseModel
from backend.entities.models.UserModel import User


class TransportPassType(Enum):
    """Enum for transport pass types"""
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"
    DAILY = "DAILY"
    YEARLY = "YEARLY"
    STUDENT = "STUDENT"
    SENIOR = "SENIOR"


class Pass(BaseModel):
    """Pass model representing the passes table"""
    id = AutoField(primary_key=True)
    type = CharField(max_length=20, null=False)  # Storing enum as string
    price = DoubleField(null=False)
    user_id = ForeignKeyField(User, backref='passes', null=False, on_delete='CASCADE')
    # Note: OneToMany relationship to Travel is handled through a backref in Travel model
    # The Travel model should have a foreign key to Pass, which we'll need to add

    class Meta:
        table_name = 'passes'
        schema = 'public'
