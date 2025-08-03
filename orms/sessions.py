from mongoengine import (
    Document, StringField, FloatField, ReferenceField, CASCADE
)

from orms.periods import Periods

class Sessions(Document):
    date = StringField(required=True)  # or DateField if you want stricter typing
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)
    courts_price = FloatField(required=True)

    meta = {"collection": "sessions"}
