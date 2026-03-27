from mongoengine import Document, StringField, FloatField, QuerySet


class Venues(Document):
    name = StringField(required=True, unique=True)
    location = StringField()
    price_per_slot = FloatField(required=True)

    meta = {"collection": "venues"}

    objects: QuerySet  # type: ignore[attr-defined]
