from mongoengine import (
    Document, IntField, DateField
)

class Periods(Document):
    start_date = DateField(required=True)
    end_date = DateField(null=True)
    total_money = IntField(null=True)

    meta = {"collection": "periods"}
