from enum import Enum
from peewee import AutoField, CharField, DoubleField, ForeignKeyField
from backend.entities.models.BaseModel import BaseModel
from backend.entities.models.UserModel import User


class TransportPassType(Enum):
    """Enum for transport pass types"""
    BKK = "BKK"
    BUBI = "BUBI"
    LIME = "LIME"
    DOTT = "DOTT"


class Pass(BaseModel):
    """Pass model representing the passes table"""
    id = AutoField(primary_key=True)
    type = CharField(max_length=20, null=False)  # Storing enum as string
    price = DoubleField(null=False)
    user_id = ForeignKeyField(User, backref='passes', null=False, on_delete='CASCADE')

    class Meta:
        table_name = 'passes'
        schema = 'public'
