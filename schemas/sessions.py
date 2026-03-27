from mongoengine import (
    Document, StringField, FloatField, ReferenceField, CASCADE, NULLIFY,
    DateField, BooleanField, QuerySet
)

from schemas.periods import Periods
from schemas.venues import Venues


class Sessions(Document):
    date = DateField(required=True, unique=True)
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)
    venue = ReferenceField(Venues, reverse_delete_rule=NULLIFY)
    slots = FloatField(default=0.0)
    is_poll_open = BooleanField(default=False)
    telegram_poll_message_id = StringField()

    meta = {"collection": "sessions"}

    objects: QuerySet  # type: ignore[attr-defined]
