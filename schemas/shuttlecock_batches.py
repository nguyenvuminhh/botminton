from mongoengine import Document, DateField, FloatField, IntField, ReferenceField, NULLIFY, QuerySet

from schemas.periods import Periods


class ShuttlecockBatches(Document):
    purchase_date = DateField(required=True, unique=True)
    total_price = FloatField(required=True)
    tube_count = IntField(required=True)
    period = ReferenceField(Periods, required=False, reverse_delete_rule=NULLIFY)

    meta = {"collection": "shuttlecock_batches", "strict": False}

    objects: QuerySet  # type: ignore[attr-defined]
