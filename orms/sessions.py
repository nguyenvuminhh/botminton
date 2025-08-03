from mongoengine import (
    Document, StringField, IntField, BooleanField,
    FloatField, DateField, ReferenceField, CASCADE
)
from datetime import datetime

class Sessions(Document):
    date = StringField(required=True)  # or DateField if you want stricter typing
    period = ReferenceField(Period, required=True, reverse_delete_rule=CASCADE)
    courts_price = FloatField(required=True)

    meta = {"collection": "sessions"}
