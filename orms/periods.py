from mongoengine import (
    Document, StringField, IntField, BooleanField,
    FloatField, DateField, ReferenceField, CASCADE
)
from datetime import datetime

class Periods(Document):
    start_date = DateField(required=True)
    end_date = DateField(null=True)
    total_money = IntField(null=True)

    meta = {"collection": "periods"}
