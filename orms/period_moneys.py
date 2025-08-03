from mongoengine import (
    Document, StringField, IntField, BooleanField,
    FloatField, DateField, ReferenceField, CASCADE
)
from datetime import datetime

from orms.periods import Periods
from orms.users import Users

class PeriodMoneys(Document):
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)
    user = ReferenceField(Users, required=True, reverse_delete_rule=CASCADE)
    amount = FloatField(required=True)

    meta = {"collection": "period_moneys"}
