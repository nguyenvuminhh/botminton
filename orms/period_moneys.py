from mongoengine import (
    Document, StringField, IntField, BooleanField,
    FloatField, DateField, ReferenceField, CASCADE
)
from datetime import datetime

class PeriodMoneys(Document):
    period = ReferenceField(Period, required=True, reverse_delete_rule=CASCADE)
    user = ReferenceField(User, required=True, reverse_delete_rule=CASCADE)
    amount = FloatField(required=True)

    meta = {"collection": "period_moneys"}
