from mongoengine import (
    Document, StringField, IntField, BooleanField,
    FloatField, DateField, ReferenceField, CASCADE
)
from datetime import datetime

class DefaultOptions(Document):
    default_location = StringField(default="Unisport")
    default_start_time = StringField(default="20:30")
    default_end_time = StringField(default="22:00")
    default_day_of_the_week_index = IntField(default=5)

    meta = {
        "collection": "default_options",
        "strict": False
    }
