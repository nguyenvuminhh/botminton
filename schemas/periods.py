from mongoengine import (
    Document, IntField, DateField, QuerySet, StringField
)

class Periods(Document):
    start_date = DateField(required=True)
    end_date = DateField(null=True)
    total_money = IntField(null=True)
    share_token = StringField(null=True, unique=True, sparse=True)

    meta = {"collection": "periods"}

    objects: QuerySet  # type: ignore[attr-defined]
