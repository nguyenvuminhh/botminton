from mongoengine import (
    Document, StringField, FloatField, ReferenceField, CASCADE, DateField, QuerySet
)

from orms.periods import Periods

class Sessions(Document):
    date = DateField(required=True, unique=True)
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)
    courts_price = FloatField(required=True)
    telegram_poll_message_id = StringField(required=True)

    meta = {"collection": "sessions"}

    objects: QuerySet  # type: ignore[attr-defined]

