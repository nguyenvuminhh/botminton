from mongoengine import Document, DateField, FloatField, IntField, ReferenceField, CASCADE, QuerySet

from schemas.periods import Periods


class ShuttlecockBatches(Document):
    purchase_date = DateField(required=True, unique=True)
    total_price = FloatField(required=True)
    tube_count = IntField()
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)

    meta = {"collection": "shuttlecock_batches"}

    objects: QuerySet  # type: ignore[attr-defined]
