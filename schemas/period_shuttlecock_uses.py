from mongoengine import CASCADE, Document, IntField, QuerySet, ReferenceField

from schemas.periods import Periods
from schemas.shuttlecock_batches import ShuttlecockBatches


class PeriodShuttlecockUses(Document):
    period = ReferenceField(Periods, required=True, reverse_delete_rule=CASCADE)
    batch = ReferenceField(ShuttlecockBatches, required=True, reverse_delete_rule=CASCADE)
    tubes_used = IntField(required=True)

    meta = {"collection": "period_shuttlecock_uses"}

    objects: QuerySet  # type: ignore[attr-defined]
